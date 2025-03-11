# TMS Auto Plan

TMS Auto Plan is a planning automation application in the transportation management system (TMS), helping to optimize the planning process and minimize travel time.

## Installation & Usage

1. **Clone the repository**
```bash
git clone https://github.com/TruongNguyen-23/tms-auto-plan.git
cd tms-auto-plan
```

2. **Create and activate virtual environment** (optional)
```bash
python -m venv env
source env/bin/activate # Windows: env\Scripts\activate
```

3. **Install libraries**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python tms.py
```
Then, access `http://localhost:5000` on the browser.

## Project Structure

```
tms-auto-plan/
├── Server/ # Server and data processing
├── blueprints/ # Flask Blueprint Structure
├── templates/ # User Interface (HTML)
├── .env # Environment Configuration
├── Dockerfile # Docker Configuration
├── app.py # Running the application
├── tms.py # Main logic processing
├── *.json # Configuration data
└── requirements.txt # List of libraries
```

## Contributions & Licenses

Contributions are welcome! Feel free to fork, create new branches, and send pull requests. The project is licensed under the **MIT License**.