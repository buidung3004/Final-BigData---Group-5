from concurrent.futures import ThreadPoolExecutor
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from typing import Optional, List, Dict

class Ratio:
    
    ratio_target = [
        "Nhóm chỉ số Định giá",
        "Nhóm chỉ số Sinh lợi",
        "Nhóm chỉ số Tăng trưởng",
        "Nhóm chỉ số thanh khoản",
        "Nhóm chỉ số Hiệu quả hoạt động",
        "Nhóm chỉ số Đòn bẩy tài chính",
        "Nhóm chỉ số Dòng tiền",
        "Cơ cấu Chi phí",
        "Cơ cấu Tài sản ngắn hạn",
        "Cơ cấu Tài sản dài hạn"
    ]

    def __init__(self):
        # Không còn cần ticker_url trong init
        chrome_options = uc.ChromeOptions()
        self.driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=chrome_options)
        # Điều hướng đến trang chủ Vietstock
        self.driver.get("https://vietstock.vn")

    def load_page(self, ticker: str):
        self.url = f"https://finance.vietstock.vn/{ticker}/tai-chinh.htm?tab=CSTC"
        self.driver.get(self.url)

    def select_period(self, period: str = "5 Kỳ"):
        try:
            period_dropdown = Select(self.driver.find_element(By.NAME, "period"))
            period_dropdown.select_by_visible_text(period)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.CDKT-row-white-color"))
            )
        except Exception as e:
            print(f"Error selecting period: {e}")

    def period_data(self) -> List[str]:
        try:
            # Đảm bảo rằng bạn tìm phần tử lại trước khi lấy dữ liệu
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#tbl-data-CSTC thead th.text-center"))
            )
            
            # Tìm lại các phần tử sau mỗi lần thay đổi DOM
            periods = self.driver.find_elements(By.CSS_SELECTOR, "table#tbl-data-CSTC thead th.text-center")
            periods_list = [period.text for period in periods if period.text]
            return periods_list
        except Exception as e:
            print(f"Error occurred while fetching periods: {e}")
            return []

    def financial_data(self) -> Dict:
        financial_data = {}
        rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.CDKT-row-white-color, tr.CDKT-header-blue-color.p1")
        current_group = None
        for row in rows:
            try:
                group_elements = row.find_elements(By.CSS_SELECTOR, "tr.CDKT-header-blue-color.p1 td.td-stockcode div.report-norm-name")
                if len(group_elements) > 0:
                    current_group = group_elements[0].text
                    continue

                indicator_name = row.find_element(By.CSS_SELECTOR, "div.report-norm-name span").text
                values = row.find_elements(By.CSS_SELECTOR, "td.text-right")
                values_list = [value.text for value in values]
                financial_data[(current_group, indicator_name)] = values_list
            except Exception as e:
                print(f"Error occurred: {e}")
        return financial_data

    def create_dataframe(self, periods_list: List[str], financial_data: Dict) -> pd.DataFrame:
        multi_index = pd.MultiIndex.from_tuples(list(financial_data.keys()), names=['Group', 'Indicator'])
        df = pd.DataFrame(list(financial_data.values()), index=multi_index, columns=periods_list)
        return df

    # Hàm này thực hiện crawling cho từng mã ticker, lấy dữ liệu và trả về ticker cùng dataframe
    def crawl_ticker_thread(self, ticker: str, period: str):
        # Bước 1: Tải trang
        self.load_page(ticker)

        # Chờ trang tải xong bằng cách đợi một phần tử cụ thể xuất hiện, ví dụ: tiêu đề bảng dữ liệu
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#tbl-data-CSTC"))
        )
        
        # Bước 2: Chọn kỳ (period)
        self.select_period(period)
        
        # Chờ 3 giây để đảm bảo kỳ đã được chọn và dữ liệu đã được tải lại
        time.sleep(3)  # Nếu bạn muốn chờ tĩnh
        
        # Bước 3: Lấy danh sách các kỳ
        periods_list = self.period_data()
        
        # Chờ thêm 2 giây để đảm bảo dữ liệu đã sẵn sàng
        time.sleep(2)

        # Bước 4: Lấy dữ liệu tài chính
        financial_data = self.financial_data()

        # Trả về ticker và dataframe đã tạo
        return ticker, self.create_dataframe(periods_list, financial_data)

    def crawl_tickers(self, tickers: List[str], period: str = "5 Kỳ"):
        """
        Crawl dữ liệu tuần tự cho nhiều mã ticker.
        """
        all_data = {}
        
        # Thực hiện crawl lần lượt từng mã ticker
        for ticker in tickers:
            print(f"Crawling data for ticker: {ticker}")
            ticker, df = self.crawl_ticker_thread(ticker, period)  # Lấy dữ liệu cho từng mã ticker
            all_data[ticker] = df  # Lưu kết quả vào dictionary
        
        return all_data

    def export_to_excel(self, data_dict: Dict[str, pd.DataFrame], file_name: str):
        with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
            for ticker, df in data_dict.items():
                df.to_excel(writer, sheet_name=ticker)
        print(f"Data exported to {file_name}")

    def login(self,
            email: Optional[str] = None,
            password: Optional[str] = None
        ):
 
        # Step 1: Try to find and click the regular login button
        try:
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'title-link btnlogin')]"))
            )
            login_button = self.driver.find_element(By.XPATH, "//a[contains(@class, 'title-link btnlogin')]")
            if login_button.is_displayed() and login_button.is_enabled():
                login_button.click()
                print("Regular login button clicked")
        except Exception:
            print("Regular login button not found, trying alternate login method")

            # Step 2: Fallback to clicking the button shown in the image (id=btn-request-call-login)
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "btn-request-call-login"))
                )
                alternate_login_button = self.driver.find_element(By.ID, "btn-request-call-login")
                if alternate_login_button.is_displayed() and alternate_login_button.is_enabled():
                    alternate_login_button.click()
                    print("Alternate login button clicked")
            except Exception as e:
                print(f"Alternate login button not found: {e}")
                return  # Stop if neither login button is found
            
        # Bước 1: Tìm và click nút đăng nhập qua Gmail, nếu có
        try:
            gmail_button = self.driver.find_element(By.XPATH, "//a[contains(@href, 'LoginGooglePlus')]")
            if gmail_button.is_displayed() and gmail_button.is_enabled():
                gmail_button.click()
                print("Gmail login button clicked")
        except Exception:
            print("Gmail button not found, assuming it's already clicked and continuing")
        
        # Bước 2: Đợi trường nhập email xuất hiện
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='email']"))
        )
        email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
        if email_input.is_displayed() and email_input.is_enabled():
            email_input.send_keys(email)
            print("Email entered")
        else:
            print("Email input field not interactable")
            return  # Dừng nếu không nhập được email

        # Bước 3: Click nút Tiếp theo sau khi nhập email
        next_button = self.driver.find_element(By.XPATH, "//span[text()='Tiếp theo']")
        if next_button.is_displayed() and next_button.is_enabled():
            next_button.click()
            print("Next button clicked after email")
        else:
            print("Next button not clickable")
            return  # Dừng nếu không click được

        # Bước 4: Đợi trường nhập mật khẩu xuất hiện
        password_input = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='password']"))
        )
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        if password_input.is_displayed() and password_input.is_enabled():
            password_input.send_keys(password)
            print("Password entered")
        else:
            print("Password input field not interactable")
            return  # Dừng nếu không nhập được mật khẩu

        # Bước 5: Click nút Tiếp theo sau khi nhập mật khẩu
        next_button = self.driver.find_element(By.XPATH, "//span[text()='Tiếp theo']")
        if next_button.is_displayed() and next_button.is_enabled():
            next_button.click()
            print("Next button clicked after password")
        else:
            print("Next button not clickable")
            return  # Dừng nếu không click được

        # Bước 6: Đợi một chút để quá trình chuyển trang diễn ra
        time.sleep(2)