# AI Course Registration Advisor 🎓🤖

A Knowledge-Based System (KBS) designed to assist Computer Science & Engineering (CSE) students at **Alamein International University (AIU)** in selecting suitable courses based on their academic progress, CGPA, and track requirements.

---

## 📌 Project Overview

This system is tailored for the **Artificial Intelligence Science** track. It provides personalized course recommendations by analyzing:

- The student’s **current semester**.
- Their **Cumulative GPA (CGPA)**.
- A list of **passed** and **failed courses**.

It ensures that university policies (e.g., credit hour limits, prerequisites) are strictly followed.

---

## 🧠 System Features

- ✅ **Knowledge Base**: Stores course info, prerequisites, co-requisites, and university policies (CSV/JSON).
- 🛠️ **Knowledge Base Editor**: Admin tool for adding/editing/deleting/viewing courses.
- 🧾 **Inference Engine** (via Experta): Uses rule-based reasoning to recommend courses.
- 🌐 **Streamlit Interface**: Simple, responsive web UI for student interaction.
- 💬 **Explanation System**: Displays reasons behind each recommendation or restriction.

---

## 🚀 How It Works

1. **Student Inputs**:
   - Semester (e.g., Fall 2025)
   - CGPA (e.g., 2.85)
   - Passed Courses (multi-select)
   - Failed Courses (multi-select)

2. **Engine Applies Rules**:
   - Checks CGPA → credit hour limit.
   - Ensures prerequisites are met.
   - Prioritizes failed courses.
   - Filters based on semester offerings.
   - Recommends only track-related courses.

3. **Outputs**:
   - Recommended Courses Table
   - Total Credit Hours
   - Explanation of each recommendation

---

## 🛠 Technologies Used

| Component              | Tech                         |
|------------------------|------------------------------|
| Interface              | Streamlit                    |
| Inference Engine       | Experta (Python Library)     |
| Data Handling          | Pandas                       |
| Knowledge Base Format  | CSV / JSON                   |
| Version Control        | Git + GitHub                 |

---

## 📂 Project Structure

```bash
.
├── app.py                   # Streamlit interface
├── inference_engine.py     # Experta-based rule engine
├── knowledge_base.csv      # Course data
├── kb_editor.py            # Admin editor for course info
├── explanations.py         # Logic for explanations
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
