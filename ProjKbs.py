import streamlit as st
import pandas as pd
from experta import *
import time
import os
import base64
import logging

# إعداد السجل لتتبع الأخطاء في ملف
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to convert file to Base64
@st.cache_data
def get_file_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found")
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

# Load the background image
background_image_path = "111.png"
try:
    img = get_file_as_base64(background_image_path)
except FileNotFoundError:
    st.error(f"Background image '{background_image_path}' not found in the project folder. Please ensure the image is in the correct directory.")
    img = ""

# CSS for background and styling with click animation
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    [data-testid="stHeader"] {{
        background: rgba(0, 0, 0, 0);
    }}
    [data-testid="stToolbar"] {{
        right: 2rem;
    }}
    [data-testid="stSidebar"] {{
        background-image: url("data:image/png;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    body {{
        background-color: transparent !important;
        color: #ffffff;
    }}
    h1 {{
        color: #ffffff;
        text-align: center;
        font-weight: 700;
        text-shadow: 2px 2px 4px #000000;
        padding-bottom: 8px;
    }}
    h2, h3 {{
        color: #ffffff;
        text-shadow: 2px 2px 4px #000000;
        padding-bottom: 8px;
    }}
    .stButton>button {{
        background-color: #1a3c34;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
        border: 1px solid #444444;
    }}
    .stButton>button:hover {{
        background-color: #14524a;
        transform: scale(1.02);
    }}
    .stButton>button:active {{
        transform: scale(0.95);
        background-color: #0f2e28;
        transition: transform 0.1s ease, background-color 0.1s ease;
    }}
    .stSelectbox, .stNumberInput, .stMultiSelect, .stTextInput {{
        background-color: rgba(68, 68, 68, 0.9);
        border-radius: 5px;
        border: 1px solid #d1d5db;
        padding: 5px;
        color: #ffffff;
    }}
    div[data-baseweb="select"] > label,
    div[data-baseweb="input"] > label,
    div[data-testid="stMultiSelect"] > label {{
        color: #ffffff !important;
        text-shadow: none;
    }}
    .stDataFrame {{
        border: 2px solid #4CAF50 !important;
        border-radius: 10px !important;
        background-color: rgba(30, 30, 30, 0.9) !important;
        color: #ffffff !important;
    }}
    .stDataFrame th {{
        background-color: #2e3b3e !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-bottom: 2px solid #4CAF50 !important;
        padding: 10px !important;
    }}
    .stDataFrame td {{
        background-color: rgba(40, 40, 40, 0.8) !important;
        color: #ffffff !important;
        padding: 8px !important;
        border: 1px solid #444444 !important;
    }}
    .st-expander {{
        background-color: rgba(30, 30, 30, 0.95) !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 10px !important;
        margin-top: 20px !important;
    }}
    .stExpander .stMarkdown {{
        color: #e0e0e0 !important;
    }}
    .stExpander .stMarkdown strong {{
        color: #4CAF50 !important;
        font-size: 16px !important;
    }}
    .stSidebar .stSelectbox {{
        background-color: rgba(68, 68, 68, 0.9);
    }}
    .stInfo, .stWarning, .stError {{
        border-radius: 5px;
        background-color: rgba(68, 68, 68, 0.9);
        color: #ffffff;
    }}
    .stMetric {{
        background-color: rgba(30, 70, 40, 0.8) !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 10px !important;
        color: white !important;
    }}
    .stMetric label {{
        color: white !important;
        font-weight: bold !important;
    }}
    .stMetric div {{
        color: #4CAF50 !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }}
    @media (max-width: 600px) {{
        .stButton>button {{
            font-size: 14px;
            padding: 8px 16px;
        }}
        h1 {{
            font-size: 24px;
        }}
    }}
    .recommended-card {{
        background-color: rgba(30, 70, 40, 0.8);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #4CAF50;
        color: #e0ffe0;
    }}
    .unavailable-card {{
        background-color: rgba(70, 30, 30, 0.8);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #ff5252;
        color: #ffe0e0;
    }}
    .admin-button-container {{
        margin-top: 30px;
        padding: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# ExplanationSystem Class
class ExplanationSystem:
    def __init__(self):
        self.explanations = []

    def add_explanation(self, message):
        try:
            self.explanations.append(message)
            logger.debug(f"Added explanation: {message}")
        except Exception as e:
            logger.error(f"Error adding explanation: {str(e)}")

    def display(self):
        if not self.explanations:
            st.info("No explanations available at this time.")
        else:
            unique_explanations = []
            seen = set()
            for exp in self.explanations:
                if exp not in seen:
                    seen.add(exp)
                    unique_explanations.append(exp)

            recommended = []
            unavailable = []

            for exp in unique_explanations:
                if "recommended" in exp.lower():
                    recommended.append(exp)
                elif "not available" in exp.lower():
                    unavailable.append(exp)

            if recommended:
                st.markdown("### ✅ Recommended Courses")
                for exp in recommended:
                    st.markdown(f"""
                    <div class="recommended-card">
                        {exp}
                    </div>
                    """, unsafe_allow_html=True)

            if unavailable:
                st.markdown("### ❌ Unavailable Courses")
                for exp in unavailable:
                    st.markdown(f"""
                    <div class="unavailable-card">
                        {exp}
                    </div>
                    """, unsafe_allow_html=True)

# KnowledgeBase Class
class KnowledgeBase:
    def __init__(self):
        self.df = self.load()

    def load(self):
        csv_file = "courses.csv"
        required_columns = ["CourseCode", "CourseName", "Prerequisites", 
                           "CoRequisites", "CreditHours", "SemesterOffered", 
                           "Track", "Level"]
        
        if not os.path.exists(csv_file):
            st.error(f"File '{csv_file}' not found. Please create it with the required columns.")
            logger.error(f"CSV file {csv_file} not found")
            return pd.DataFrame(columns=required_columns)

        try:
            df = pd.read_csv(csv_file)
            df = df.rename(columns={
                "Course Code": "CourseCode",
                "Course Name": "CourseName",
                "Credit Hours": "CreditHours",
                "Semester Offered": "SemesterOffered",
                "Co-requisites": "CoRequisites"
            })
            for col in required_columns:
                if col not in df.columns:
                    df[col] = "" if col in ["Prerequisites", "CoRequisites"] else \
                              0 if col == "CreditHours" else \
                              "Unknown" if col == "Level" else \
                              "Unknown"
            df = df.dropna(subset=["CourseCode"])
            df["CourseCode"] = df["CourseCode"].astype(str)
            df = df.replace('nan', '')
            df["Prerequisites"] = df["Prerequisites"].fillna("")
            df["CoRequisites"] = df["CoRequisites"].fillna("")
            df["SemesterOffered"] = df["SemesterOffered"].fillna("Both").astype(str).str.strip().str.title()
            df["SemesterOffered"] = df["SemesterOffered"].replace(
                {"": "Both", "Unknown": "Both", "None": "Both", "Nan": "Both"}
            )
            valid_semesters = ["Fall", "Spring", "Both"]
            df["SemesterOffered"] = df["SemesterOffered"].apply(
                lambda x: x if x in valid_semesters else "Both"
            )
            df["CreditHours"] = pd.to_numeric(df["CreditHours"], errors="coerce").fillna(3).astype(int)
            df["Track"] = df["Track"].fillna("Big Data Analytics")
            df["Level"] = df["Level"].fillna("Unknown")
            df = df.drop_duplicates(subset=["CourseCode"], keep="first")
            logger.info(f"Loaded {len(df)} courses from {csv_file} after removing duplicates")
            return df[required_columns]
        except Exception as e:
            st.error(f"Error reading file {csv_file}: {str(e)}")
            logger.error(f"Error reading CSV {csv_file}: {str(e)}")
            return pd.DataFrame(columns=required_columns)

    def save_to_csv(self, file_name):
        try:
            self.df.to_csv(file_name, index=False)
            if os.path.exists(file_name):
                mod_time = os.path.getmtime(file_name)
                current_time = time.time()
                if current_time - mod_time < 5:
                    st.success(f"Data successfully saved to '{file_name}'!")
                    logger.info(f"Saved data to {file_name}")
                    return True
                else:
                    st.error(f"File '{file_name}' was not updated. It might be open or locked.")
                    logger.error(f"File {file_name} not updated")
                    return False
            else:
                st.error(f"File '{file_name}' was not created. Check disk space or folder permissions.")
                logger.error(f"File {file_name} not created")
                return False
        except PermissionError as e:
            st.error(f"Cannot save to '{file_name}' due to permission issues: {str(e)}")
            logger.error(f"Permission error saving {file_name}: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Failed to save data to '{file_name}': {str(e)}")
            logger.error(f"Error saving {file_name}: {str(e)}")
            return False

    def save(self):
        return self.save_to_csv("courses.csv")

    def validate_course(self, course_data):
        try:
            if not course_data["CourseCode"]:
                raise ValueError("Course Code cannot be empty!")
            if not course_data["CourseName"]:
                raise ValueError("Course Name cannot be empty!")
            if course_data["CreditHours"] <= 0:
                raise ValueError("Credit Hours must be a positive integer!")
            prereqs = course_data["Prerequisites"].split(",") if course_data["Prerequisites"] else []
            coreqs = course_data["CoRequisites"].split(",") if course_data["CoRequisites"] else []
            if course_data["CourseCode"] in prereqs or course_data["CourseCode"] in coreqs:
                raise ValueError("Course cannot be a prerequisite or corequisite of itself!")
            valid_codes = self.df["CourseCode"].tolist()
            for prereq in prereqs:
                if prereq.strip() and prereq.strip() not in valid_codes:
                    raise ValueError(f"Invalid prerequisite: {prereq}")
            for coreq in coreqs:
                if coreq.strip() and coreq.strip() not in valid_codes:
                    raise ValueError(f"Invalid co-requisite: {coreq}")
        except Exception as e:
            logger.error(f"Error validating course data: {str(e)}")
            raise

    def add_course(self, course_data):
        try:
            if course_data["CourseCode"] in self.df["CourseCode"].values:
                raise ValueError("Course Code already exists!")
            self.validate_course(course_data)
            self.df = pd.concat([self.df, pd.DataFrame([course_data])], ignore_index=True)
            if self.save():
                st.success(f"Course '{course_data['CourseCode']}' added successfully!")
                logger.info(f"Added course {course_data['CourseCode']}")
            else:
                raise ValueError("Failed to save the new course to the CSV file.")
        except Exception as e:
            st.error(f"Error adding course: {str(e)}")
            logger.error(f"Error adding course: {str(e)}")
            raise

    def edit_course(self, course_code, course_data):
        try:
            if course_code not in self.df["CourseCode"].values:
                raise ValueError("Course Code does not exist!")
            self.validate_course(course_data)
            self.df.loc[self.df["CourseCode"] == course_code, ["CourseName", "Prerequisites", 
                "CoRequisites", "CreditHours", "SemesterOffered", "Track", "Level"]] = \
                [course_data["CourseName"], course_data["Prerequisites"], 
                 course_data["CoRequisites"], course_data["CreditHours"], course_data["SemesterOffered"], 
                 course_data["Track"], course_data["Level"]]
            if self.save():
                st.success(f"Course '{course_code}' updated successfully!")
                logger.info(f"Updated course {course_code}")
            else:
                raise ValueError("Failed to save the updated course to the CSV file.")
        except Exception as e:
            st.error(f"Error editing course: {str(e)}")
            logger.error(f"Error editing course: {str(e)}")
            raise

    def delete_course(self, course_code):
        try:
            if course_code not in self.df["CourseCode"].values:
                raise ValueError("Course Code does not exist!")
            for _, row in self.df.iterrows():
                prereqs = row["Prerequisites"].split(",") if row["Prerequisites"] else []
                coreqs = row["CoRequisites"].split(",") if row["CoRequisites"] else []
                if course_code in prereqs or course_code in coreqs:
                    raise ValueError(f"Cannot delete {course_code} as it is a prerequisite or corequisite for another course!")
            self.df = self.df[self.df["CourseCode"] != course_code].reset_index(drop=True)
            if self.save():
                st.success(f"Course '{course_code}' deleted successfully!")
                logger.info(f"Deleted course {course_code}")
            else:
                raise ValueError("Failed to save the changes after deleting the course.")
        except Exception as e:
            st.error(f"Error deleting course: {str(e)}")
            logger.error(f"Error deleting course: {str(e)}")
            raise

    def editor(self):
        st.subheader("Knowledge Base Editor")
        st.markdown("Use this section to manage the course catalog for the Big Data Analytics track.")
        if self.df.empty:
            st.warning("No courses available. Please add a new course.")

        if "admin_action" not in st.session_state:
            st.session_state.admin_action = None

        if st.session_state.admin_action is None:
            st.markdown("### Select an Action")
            st.markdown('<div class="admin-button-container">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                if st.button("📊 View Courses", use_container_width=True):
                    st.session_state.admin_action = "View Courses"
                    st.rerun()
            with col2:
                if st.button("➕ Add Course", use_container_width=True):
                    st.session_state.admin_action = "Add Course"
                    st.rerun()
            with col3:
                if st.button("✏️ Edit Course", use_container_width=True):
                    st.session_state.admin_action = "Edit Course"
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete Course", use_container_width=True):
                    st.session_state.admin_action = "Delete Course"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            if st.session_state.admin_action == "View Courses":
                st.markdown("### View Courses")
                styled_df = self.df.style.set_properties(**{
                    'background-color': '#1c2526',
                    'color': '#ffffff',
                    'border-color': '#ffffff',
                    'text-align': 'left',
                    'padding': '8px'
                }).set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#2e3b3e'),
                        ('color', '#ffffff'),
                        ('font-weight', 'bold'),
                        ('padding', '10px'),
                        ('border-bottom', '2px solid #ffffff')
                    ]}
                ])
                st.dataframe(styled_df, use_container_width=True)
                if st.button("⬅️ Back"):
                    st.session_state.admin_action = None
                    st.rerun()

            elif st.session_state.admin_action == "Add Course":
                st.markdown("### Add New Course")
                with st.form("add_course_form"):
                    course_code = st.text_input("Course Code (e.g., CSE101)")
                    course_name = st.text_input("Course Name")
                    course_options = self.df["CourseCode"].tolist()
                    selected_prereqs = st.multiselect("Prerequisites", course_options)
                    prerequisites = ",".join(selected_prereqs) if selected_prereqs else ""
                    selected_coreqs = st.multiselect("Co-requisites", course_options)
                    corequisites = ",".join(selected_coreqs) if selected_coreqs else ""
                    credit_hours = st.number_input("Credit Hours", min_value=1, step=1)
                    semester_offered = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"])
                    track = st.selectbox("Track", ["All", "Big Data Analytics"])
                    level = st.selectbox("Level", ["1", "2", "3", "4"])
                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("Add Course")
                    with col2:
                        cancel = st.form_submit_button("Cancel")

                    if submit:
                        try:
                            course_data = {
                                "CourseCode": course_code,
                                "CourseName": course_name,
                                "Prerequisites": prerequisites,
                                "CoRequisites": corequisites,
                                "CreditHours": credit_hours,
                                "SemesterOffered": semester_offered,
                                "Track": track,
                                "Level": level
                            }
                            self.add_course(course_data)
                            st.session_state.admin_action = None
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                    if cancel:
                        st.session_state.admin_action = None
                        st.rerun()
                if st.button("⬅️ Back"):
                    st.session_state.admin_action = None
                    st.rerun()

            elif st.session_state.admin_action == "Edit Course":
                st.markdown("### Edit Course")
                course_code = st.selectbox("Select Course to Edit", self.df["CourseCode"])
                course_data = self.df[self.df["CourseCode"] == course_code].iloc[0]

                with st.form("edit_course_form"):
                    course_name = st.text_input("Course Name", value=course_data["CourseName"])
                    course_options = self.df["CourseCode"].tolist()
                    current_prereqs = course_data["Prerequisites"].split(",") if course_data["Prerequisites"] else []
                    selected_prereqs = st.multiselect("Prerequisites", course_options, default=[p for p in current_prereqs if p])
                    prerequisites = ",".join(selected_prereqs) if selected_prereqs else ""
                    current_coreqs = course_data["CoRequisites"].split(",") if course_data["CoRequisites"] else []
                    selected_coreqs = st.multiselect("Co-requisites", course_options, default=[c for c in current_coreqs if c])
                    corequisites = ",".join(selected_coreqs) if selected_coreqs else ""
                    credit_hours = st.number_input("Credit Hours", min_value=1, step=1, value=int(course_data["CreditHours"]))
                    semester_offered = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"], 
                                                    index=["Fall", "Spring", "Both"].index(course_data["SemesterOffered"]))
                    track = st.selectbox("Track", ["All", "Big Data Analytics"], 
                                         index=["All", "Big Data Analytics"].index(course_data["Track"]))
                    level = st.selectbox("Level", ["1", "2", "3", "4"], 
                                         index=["1", "2", "3", "4"].index(str(course_data["Level"])))
                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("Update Course")
                    with col2:
                        cancel = st.form_submit_button("Cancel")

                    if submit:
                        try:
                            updated_data = {
                                "CourseCode": course_code,
                                "CourseName": course_name,
                                "Prerequisites": prerequisites,
                                "CoRequisites": corequisites,
                                "CreditHours": credit_hours,
                                "SemesterOffered": semester_offered,
                                "Track": track,
                                "Level": level
                            }
                            self.edit_course(course_code, updated_data)
                            st.session_state.admin_action = None
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                    if cancel:
                        st.session_state.admin_action = None
                        st.rerun()
                if st.button("⬅️ Back"):
                    st.session_state.admin_action = None
                    st.rerun()

            elif st.session_state.admin_action == "Delete Course":
                st.markdown("### Delete Course")
                course_code = st.selectbox("Select Course to Delete", self.df["CourseCode"])
                col1, col2 = st.columns(2)
                with col1:
                    confirm = st.checkbox("Confirm deletion")
                with col2:
                    delete_button = st.button("Delete Course")
                    if delete_button and confirm:
                        try:
                            self.delete_course(course_code)
                            st.session_state.admin_action = None
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                if st.button("⬅️ Back"):
                    st.session_state.admin_action = None
                    st.rerun()

# RecommendationEngine Class
class Course(Fact):
    pass

class Student(Fact):
    pass

class RecommendationState(Fact):
    pass

class RecommendationEngine(KnowledgeEngine):
    def __init__(self, semester, cgpa, passed_courses, failed_courses, kb, explanation_system, level, track="Big Data Analytics"):
        super().__init__()
        self.semester = semester
        self.cgpa = cgpa
        self.passed_courses = passed_courses or []
        self.failed_courses = failed_courses or []
        self.kb = kb
        self.explanation_system = explanation_system
        self.track = track
        self.level = level

        try:
            self.reset()
            self.declare(Student(
                cgpa=cgpa,
                passed=self.passed_courses,
                failed=self.failed_courses,
                level=level
            ))
            self.declare(RecommendationState(
                courses=[],
                total_credits=0
            ))
            if not kb.empty:
                for _, row in kb.iterrows():
                    if row["Track"] in (self.track, "All") and row["SemesterOffered"] in (self.semester, "Both"):
                        self.declare(Course(
                            code=row["CourseCode"],
                            name=row["CourseName"],
                            prerequisites=row["Prerequisites"].split(",") if row["Prerequisites"] else [],
                            corequisites=row["CoRequisites"].split(",") if row["CoRequisites"] else [],
                            credits=int(row["CreditHours"]),
                            semester=str(row["SemesterOffered"]),
                            level=row["Level"]
                        ))
            else:
                logger.warning("Knowledge base is empty. No courses to declare.")
        except Exception as e:
            logger.error(f"Error initializing RecommendationEngine: {str(e)}")
            st.error(f"Failed to initialize recommendation engine: {str(e)}")

    @DefFacts()
    def _initial_facts(self):
        try:
            if self.cgpa < 2.0:
                yield Fact(credit_limit=12)
            elif self.cgpa < 3.0:
                yield Fact(credit_limit=15)
            else:
                yield Fact(credit_limit=18)
        except Exception as e:
            logger.error(f"Error in _initial_facts: {str(e)}")

    @Rule(
        Fact(credit_limit=MATCH.limit),
        Course(
            code=MATCH.code,
            name=MATCH.name,
            prerequisites=MATCH.prereqs,
            corequisites=MATCH.coreqs,
            credits=MATCH.credits,
            semester=MATCH.sem,
            level=MATCH.course_level
        ),
        Student(passed=MATCH.passed, failed=MATCH.failed, level=MATCH.student_level),
        RecommendationState(courses=MATCH.courses, total_credits=MATCH.total_credits),
        TEST(lambda prereqs, passed: all(p.strip() in passed or p.strip() == "" for p in prereqs)),
        TEST(lambda coreqs, passed, courses: all(c.strip() in passed or c.strip() in [r[0] for r in courses] or c.strip() == "" for c in coreqs)),
        TEST(lambda credits, limit, total_credits: total_credits + credits <= limit),
        TEST(lambda code, failed: code in failed),
        TEST(lambda code, courses: code not in [c[0] for c in courses]),
        TEST(lambda course_level, student_level: int(course_level) <= int(student_level)),
        salience=5
    )
    def recommend_failed_course(self, code, name, credits, course_level, courses, total_credits):
        try:
            new_courses = list(courses) + [[code, name, credits, course_level]]
            new_total_credits = total_credits + credits
            for fact_id, fact in self.facts.items():
                if isinstance(fact, RecommendationState):
                    self.modify(self.facts[fact_id], 
                                courses=new_courses, 
                                total_credits=new_total_credits)
                    self.explanation_system.add_explanation(
                        f"{code} is recommended because you failed it previously and its prerequisites are met. "
                        f"Course Level: {course_level}, Your Level: {self.level}."
                    )
                    logger.debug(f"Recommended failed course: {code}")
                    break
            else:
                logger.error("No RecommendationState fact found")
                st.error("Failed to update recommendations: RecommendationState not found")
        except Exception as e:
            logger.error(f"Error in recommend_failed_course: {str(e)}")
            st.error(f"Error recommending failed course: {str(e)}")

    @Rule(
        Fact(credit_limit=MATCH.limit),
        Course(
            code=MATCH.code,
            name=MATCH.name,
            prerequisites=MATCH.prereqs,
            corequisites=MATCH.coreqs,
            credits=MATCH.credits,
            semester=MATCH.sem,
            level=MATCH.course_level
        ),
        Student(passed=MATCH.passed, failed=MATCH.failed, level=MATCH.student_level),
        RecommendationState(courses=MATCH.courses, total_credits=MATCH.total_credits),
        TEST(lambda prereqs, passed: all(p.strip() in passed or p.strip() == "" for p in prereqs)),
        TEST(lambda coreqs, passed, courses: all(c.strip() in passed or c.strip() in [r[0] for r in courses] or c.strip() == "" for c in coreqs)),
        TEST(lambda credits, limit, total_credits: total_credits + credits <= limit),
        TEST(lambda code, passed, failed: code not in passed and code not in failed),
        TEST(lambda code, courses: code not in [c[0] for c in courses]),
        TEST(lambda course_level, student_level: int(course_level) <= int(student_level)),
        salience=5
    )
    def recommend_new_course(self, code, name, credits, prereqs, course_level, courses, total_credits):
        try:
            new_courses = list(courses) + [[code, name, credits, course_level]]
            new_total_credits = total_credits + credits
            for fact_id, fact in self.facts.items():
                if isinstance(fact, RecommendationState):
                    self.modify(self.facts[fact_id], 
                                courses=new_courses, 
                                total_credits=new_total_credits)
                    self.explanation_system.add_explanation(
                        f"{code} is recommended because you passed its prerequisites: "
                        f"{', '.join(prereqs) if prereqs else 'None'}. "
                        f"Course Level: {course_level}, Your Level: {self.level}."
                    )
                    logger.debug(f"Recommended new course: {code}")
                    break
            else:
                logger.error("No RecommendationState fact found")
                st.error("Failed to update recommendations: RecommendationState not found")
        except Exception as e:
            logger.error(f"Error in recommend_new_course: {str(e)}")
            st.error(f"Error recommending new course: {str(e)}")

    @Rule(
        Course(
            code=MATCH.code,
            prerequisites=MATCH.prereqs
        ),
        Student(passed=MATCH.passed),
        TEST(lambda prereqs, passed: any(p.strip() not in passed and p.strip() != "" for p in prereqs))
    )
    def unmet_prerequisites(self, code, prereqs, passed):
        try:
            unmet = [p.strip() for p in prereqs if p.strip() not in passed and p.strip() != ""]
            self.explanation_system.add_explanation(
                f"{code} is not available due to unmet prerequisites: {', '.join(unmet)}."
            )
            logger.debug(f"Unmet prerequisites for {code}: {unmet}")
        except Exception as e:
            logger.error(f"Error in unmet_prerequisites: {str(e)}")

    def get_recommendations(self):
        try:
            self.run()
            for fact_id, fact in self.facts.items():
                if isinstance(fact, RecommendationState):
                    if 'courses' in fact:
                        seen_codes = set()
                        unique_courses = []
                        for course in fact['courses']:
                            code = course[0]
                            if code not in seen_codes:
                                seen_codes.add(code)
                                unique_courses.append(course)
                        logger.debug(f"Returning deduplicated recommendations: {unique_courses}")
                        return unique_courses
                    else:
                        logger.error("RecommendationState fact does not have 'courses' attribute")
                        st.error("RecommendationState missing 'courses' attribute")
                        return []
            logger.warning("No RecommendationState fact found in get_recommendations")
            return []
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            st.error(f"Failed to get recommendations: {str(e)}")
            return []

# StudentInterface Class
class StudentInterface:
    def __init__(self, kb, explanation_system):
        self.kb = kb.df
        self.explanation_system = explanation_system

    def render(self):
        st.title("AIU CSE Course Registration Advising System")
        st.markdown("### Welcome to the Course Advising System for the Big Data Analytics Track")
        st.info("""
        This system helps you select courses for the upcoming semester based on your academic progress. 
        Please provide your details below to receive personalized recommendations.
        """)

        # Move inputs to the sidebar
        with st.sidebar:
            with st.form("student_form"):
                st.markdown("#### Enter Your Academic Details")
                semester = st.selectbox("Current Semester", ["Fall", "Spring"])
                cgpa = st.number_input("CGPA (0.0–4.0)", min_value=0.0, max_value=4.0, step=0.1)
                level = st.selectbox("Your Current Level", ["1", "2", "3", "4"])
                
                if not self.kb.empty:
                    # Create formatted course options with only code and level
                    course_options = [
                        f"{row['CourseCode']} - Level {row['Level']}"
                        for _, row in self.kb.iterrows()
                    ]
                    course_code_map = {
                        f"{row['CourseCode']} - Level {row['Level']}": row['CourseCode']
                        for _, row in self.kb.iterrows()
                    }
                    
                    # Passed Courses multiselect
                    selected_passed = st.multiselect("Passed Courses", course_options)
                    passed_courses = [course_code_map[course] for course in selected_passed]
                    
                    # Failed Courses multiselect (exclude passed courses)
                    available_failed_options = [
                        course for course in course_options 
                        if course_code_map[course] not in passed_courses
                    ]
                    selected_failed = st.multiselect("Failed Courses", available_failed_options)
                    failed_courses = [course_code_map[course] for course in selected_failed]
                else:
                    passed_courses = []
                    failed_courses = []
                    st.warning("No courses available in the Knowledge Base. Please contact the admin to add courses.")

                submit = st.form_submit_button("Get Recommendations")

        # Main content for recommendations
        if 'submit' in locals() and submit:
            try:
                if not 0.0 <= cgpa <= 4.0:
                    st.error("CGPA must be between 0.0 and 4.0!")
                    logger.error("Invalid CGPA input")
                    return
                if self.kb.empty:
                    st.error("No courses available in the Knowledge Base! Please use Admin Mode to add courses.")
                    logger.error("Empty knowledge base")
                    return
                if any(course in passed_courses for course in failed_courses):
                    st.error("A course cannot be both passed and failed! Please correct your selections.")
                    logger.error("Conflicting course selections")
                    return

                if cgpa < 2.0:
                    max_credits = 12
                elif cgpa < 3.0:
                    max_credits = 15
                else:
                    max_credits = 18

                with st.spinner("Generating recommendations..."):
                    time.sleep(1)
                    engine = RecommendationEngine(semester, cgpa, passed_courses, failed_courses, 
                                                self.kb, self.explanation_system, level)
                    recommendations = engine.get_recommendations()

                if not recommendations:
                    st.warning("No courses are available based on your inputs. Consider adjusting your CGPA, passed courses, or failed courses.")
                    logger.warning("No recommendations generated")
                else:
                    st.subheader("Recommended Courses for Your Semester")
                    rec_df = pd.DataFrame(recommendations, columns=["Course Code", "Course Name", "Credit Hours", "Level"])
                    st.dataframe(
                        rec_df.style
                            .set_properties(**{
                                'background-color': 'rgba(40, 40, 40, 0.8)',
                                'color': 'white',
                                'border-color': '#4CAF50'
                            })
                            .set_table_styles([{
                                'selector': 'th',
                                'props': [
                                    ('background-color', '#2e3b3e'),
                                    ('color', 'white'),
                                    ('font-weight', 'bold'),
                                    ('border-bottom', '2px solid #4CAF50')
                                ]
                            }]),
                        use_container_width=True
                    )
                    recommended_credits = sum([row[2] for row in recommendations])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Maximum Credit Hours", max_credits)
                    with col2:
                        st.metric("Recommended Credit Hours", recommended_credits)
                    logger.info(f"Generated {len(recommendations)} recommendations, recommended credits: {recommended_credits}, max credits: {max_credits}")

                    with st.expander("View Explanations"):
                        self.explanation_system.display()

                # Add Report button at the bottom of the main content
                st.markdown("### Report")
                report_file = "Report.pdf"
                report_data = get_file_as_base64(report_file)
                if report_data:
                    st.download_button(
                        label="📄 View Report",
                        data=base64.b64decode(report_data),
                        file_name=report_file,
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error(f"Report file '{report_file}' not found.")

            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")
                logger.error(f"Error in student interface: {str(e)}")

# Main Function with Welcome Page
def main():
    logger.debug(f"Current working directory: {os.getcwd()}")
    if "mode_selected" not in st.session_state:
        st.session_state.mode_selected = None

    if not st.session_state.mode_selected:
        st.title("AIU CSE Course Registration Advising System")
        st.markdown("### Welcome to the Course Advising System!")
        st.info("Please select your role to proceed:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Student Mode"):
                st.session_state.mode_selected = "Student Mode"
                st.rerun()
        with col2:
            if st.button("Admin Mode"):
                st.session_state.mode_selected = "Admin Mode"
                st.rerun()

    else:
        try:
            kb = KnowledgeBase()
            explanation_system = ExplanationSystem()
            student_interface = StudentInterface(kb, explanation_system)

            st.sidebar.header("Mode")
            mode = st.sidebar.selectbox("Select Mode", ["Student Mode", "Admin Mode"], 
                                        index=0 if st.session_state.mode_selected == "Student Mode" else 1)

            if mode != st.session_state.mode_selected:
                st.session_state.mode_selected = mode
                st.rerun()

            if mode == "Admin Mode":
                st.sidebar.markdown("### Admin Mode: Manage Knowledge Base")
                password = st.sidebar.text_input("Enter Admin Password", type="password")
                if password == "admin123":
                    kb.editor()
                else:
                    st.sidebar.error("Incorrect password! Please try again.")
                    logger.error("Incorrect admin password")
            else:
                st.sidebar.markdown("### Student Mode: Get Course Recommendations")
                student_interface.render()
        except Exception as e:
            st.error(f"Error in main function: {str(e)}")
            logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
