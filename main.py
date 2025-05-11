import requests
import json
from datetime import datetime

def get_user_details():
    """Get validated user input for registration"""
    print("\n" + "="*50)
    print("Employee Data Analysis System")
    print("="*50)
    
    while True:
        name = input("Enter your full name: ").strip()
        if name:
            break
        print("Name cannot be empty. Please try again.")
    
    while True:
        reg_no = input("Enter your registration number (e.g., REG12345): ").strip().upper()
        if reg_no.startswith("REG") and reg_no[3:].isdigit() and len(reg_no) > 3:
            break
        print("Invalid format. Must start with REG followed by numbers (e.g., REG12345)")
    
    while True:
        email = input("Enter your email address: ").strip()
        if "@" in email and "." in email.split("@")[-1]:
            break
        print("Please enter a valid email address (e.g., user@example.com)")
    
    return {
        "name": name,
        "regNo": reg_no,
        "email": email
    }

def generate_problem1_solution():
    """SQL solution for Problem 1: Highest salary not on 1st of month"""
    return """
    SELECT 
        p.AMOUNT AS SALARY,
        CONCAT(e.FIRST_NAME, ' ', e.LAST_NAME) AS NAME,
        FLOOR(DATEDIFF(CURDATE(), e.DOB)/365) AS AGE,
        d.DEPARTMENT_NAME
    FROM 
        PAYMENTS p
    JOIN 
        EMPLOYEE e ON p.EMP_ID = e.EMP_ID
    JOIN 
        DEPARTMENT d ON e.DEPARTMENT = d.DEPARTMENT_ID
    WHERE 
        DAY(p.PAYMENT_TIME) != 1
    ORDER BY 
        p.AMOUNT DESC
    LIMIT 1;
    """

def generate_problem2_solution():
    """SQL solution for Problem 2: Younger employees count by department"""
    return """
    SELECT 
        e.EMP_ID,
        e.FIRST_NAME,
        e.LAST_NAME,
        d.DEPARTMENT_NAME,
        (
            SELECT COUNT(*) 
            FROM EMPLOYEE e2 
            WHERE e2.DEPARTMENT = e.DEPARTMENT 
            AND e2.DOB > e.DOB
        ) AS YOUNGER_EMPLOYEES_COUNT
    FROM 
        EMPLOYEE e
    JOIN 
        DEPARTMENT d ON e.DEPARTMENT = d.DEPARTMENT_ID
    ORDER BY 
        e.EMP_ID DESC;
    """

def submit_solution(webhook_url, auth_token, sql_query):
    """Submit the final SQL query to the webhook"""
    try:
        response = requests.post(
            webhook_url,
            json={"finalQuery": sql_query.strip()},
            headers={
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return True, response.text
    except Exception as e:
        return False, str(e)

def main():
    user_data = get_user_details()
    
    try:
        print("\nConnecting to server to generate webhook...")
        response = requests.post(
            "https://bfhldevapigw.healthrx.co.in/hiring/generateWebhook/PYTHON",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        webhook_data = response.json()
        
        webhook_url = webhook_data["webhook"]
        auth_token = webhook_data["accessToken"]
        print("\n✔ Webhook successfully generated")
        print(f"Webhook URL: {webhook_url[:60]}...")
        print(f"Auth Token: {auth_token[:15]}...")

        last_digit = int(user_data["regNo"][-1])
        is_even = last_digit % 2 == 0
        
        if is_even:
            print("\nSolving Problem 2: Younger employees count by department")
            sql_solution = generate_problem2_solution()
        else:
            print("\nSolving Problem 1: Highest salary not on 1st of month")
            sql_solution = generate_problem1_solution()
        
        print("\nGenerated SQL Query:")
        print("-"*80)
        print(sql_solution.strip())
        print("-"*80)

        print("\nSubmitting solution to webhook...")
        success, result = submit_solution(webhook_url, auth_token, sql_solution)
        
        if success:
            print("\n✅ Successfully submitted solution!")
            print("Server response:", result)
        else:
            print("\n❌ Failed to submit solution")
            print("Error:", result)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {str(e)}")
    except json.JSONDecodeError:
        print("\n❌ Invalid server response format")
    except KeyError:
        print("\n❌ Missing required data in server response")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("\nError: The 'requests' package is required.")
        print("Please install it by running: pip install requests")
        exit(1)
    
    main()
