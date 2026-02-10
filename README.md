# Smart Municipal Service System

## Project Overview
A web-based application for managing municipal services, built with **Django** (Python) and **Bootstrap 5**. The system serves Citizens, Office Admins, Section Users, and Spokespersons.

## 6. Resource Requirements

### 6.1 Hardware requirements
**A. Development workstation:**
*   PC with Intel i5 or equivalent.
*   Minimum 8 GB RAM (16 GB recommended).
*   Sufficient storage for tools/files.

**B. Internet connection:**
*   Stable, high-speed connection for installing packages (Django, Python), version control (GitHub), and updates.

**G. Server:**
*   1–2 GB RAM
*   20 GB SSD storage
*   1 vCPU
*   Support for Python/Django deployments

### 6.2 Software requirements
**A. Project management tools:**
*   Trello (External)

**B. Frontend development:**
*   **HTML5 & CSS3**: Core structure (Templates).
*   **Bootstrap**: CSS Framework (v5 via CDN).
*   **Visual Studio Code**: Recommended IDE.

**C. Backend development:**
*   **Python**: Runtime environment.
*   **Django Framework**: Core backend (v5.x/6.x).
*   **Django Admin Panel**: Built-in management.

**D. Database management:**
*   **MySQL**: Supported (Requires `mysqlclient`).
    *   *Note: Default configuration is set to SQLite for development ease. To use MySQL, update `DATABASES` in `settings.py`.*

**E. Version control:**
*   Git & GitHub.

**F. Testing tools:**
*   Postman (For future API endpoints).
*   Browser Developer Tools.

## Setup Instructions

1.  **Install Python**: Ensure Python (3.10+) is installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Migration**:
    ```bash
    python manage.py migrate
    ```
4.  **Load Initial Data**:
    ```bash
    python manage.py setup_data
    ```
5.  **Run Server**:
    ```bash
    python manage.py runserver
    ```
6.  **Access**: `http://127.0.0.1:8000/`

## User Accounts (Demo)
*   **Citizen**: `citizen` / `password`
*   **Section User**: `section_user` / `password`
*   **Office Admin**: `office_admin` / `password`
*   **Spokesperson**: `spokesperson` / `password`
*   **Super Admin**: `admin` / `admin123`
