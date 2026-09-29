# Zero-GNSS VIO-SLAM Navigation & Risk Dashboard

This repository contains the live demo vehicle control and risk dashboard powered by **DynaFusion-VIO**.

## Setup & Running Instructions

1. **Extract and Navigate:**
   ```bash
   cd sih_vioslam_dashboard
   ```

2. **Create Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Live Dashboard:**
   ```bash
   streamlit run app.py
   ```
