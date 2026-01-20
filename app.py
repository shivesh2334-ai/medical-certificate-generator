import streamlit as st
from datetime import datetime, date
from fpdf import FPDF
import os
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile

# Page config - MUST BE FIRST!
st.set_page_config(
    page_title="Medical Certificate Generator",
    page_icon="🏥",
    layout="wide"
)

# Create necessary directories
Path("certificates").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .cert-type-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #764ba2;
        transform: translateY(-2px);
    }
    .required-field::after {
        content: " *";
        color: red;
    }
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 1px solid #e0e0e0;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to create stamp image
def create_stamp_image():
    """Create a medical stamp image if it doesn't exist"""
    stamp_path = "static/stamp.png"
    if not os.path.exists(stamp_path):
        try:
            # Create a rectangular stamp image
            width, height = 300, 120
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle([(0, 0), (width-1, height-1)], 
                         outline=(200, 0, 0, 255), width=2)
            
            # Add inner border
            draw.rectangle([(10, 10), (width-11, height-11)], 
                         outline=(200, 0, 0, 255), width=1)
            
            try:
                # Try to use a bold font
                font_large = ImageFont.truetype("arialbd.ttf", 20)
                font_small = ImageFont.truetype("arial.ttf", 14)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add text
            draw.text((width/2, 30), "MEDICAL STAMP", 
                     fill=(200, 0, 0, 255), font=font_large, anchor="mm")
            draw.text((width/2, 60), "Authorized Signatory", 
                     fill=(150, 0, 0, 255), font=font_small, anchor="mm")
            draw.text((width/2, 85), "Clinic Seal", 
                     fill=(150, 0, 0, 255), font=font_small, anchor="mm")
            
            # Save the image
            image.save(stamp_path, "PNG")
        except Exception as e:
            st.warning(f"Could not create stamp image: {str(e)}")
            return False
    return True

# Create stamp image
create_stamp_image()

# PDF Generation Functions
class MedicalPDF(FPDF):
    """Custom PDF class for medical certificates"""
    
    def add_clinic_header(self, clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg):
        """Add clinic header to PDF"""
        self.set_font("Arial", "B", 20)
        self.cell(0, 10, clinic_name, 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, clinic_address, 0, "C")
        self.cell(0, 5, f"Phone: {clinic_phone} | Email: {clinic_email}", 0, 1, "C")
        if clinic_reg:
            self.cell(0, 5, f"Registration No: {clinic_reg}", 0, 1, "C")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def add_signature_section(self, doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty):
        """Add signature section with stamp"""
        self.ln(15)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, "Place: _________________", 0, 1)
        self.cell(0, 6, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
        self.ln(10)
        
        # Doctor's details aligned to right
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, f"Dr. {doctor_name}", 0, 1, "R")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, doctor_qualification, 0, 1, "R")
        if doctor_reg_no:
            self.cell(0, 5, f"Reg. No: {doctor_reg_no}", 0, 1, "R")
        if doctor_specialty:
            self.cell(0, 5, doctor_specialty, 0, 1, "R")
        
        # Add stamp if exists
        stamp_path = "static/stamp.png"
        if os.path.exists(stamp_path):
            try:
                # Position stamp centered
                stamp_x = (210 - 40) / 2  # Center of A4 page (210mm width)
                stamp_y = self.get_y() + 5
                self.image(stamp_path, x=stamp_x, y=stamp_y, w=40)
                self.ln(25)
            except Exception as e:
                print(f"Error adding stamp: {e}")
        
        # Footer note
        self.set_y(-30)
        self.set_font("Arial", "I", 8)
        self.cell(0, 5, "This is a computer-generated certificate and requires doctor's signature and official seal to be valid.", 0, 1, "C")

def generate_medical_certificate(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                                 doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                                 patient_name, patient_age, patient_gender, patient_designation,
                                 patient_office, exam_date, medical_condition, leave_from, leave_to, notes):
    
    pdf = MedicalPDF()
    pdf.add_page()
    
    # Add clinic header
    pdf.add_clinic_header(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MEDICAL CERTIFICATE", 0, 1, "C")
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date: {exam_date.strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, f"This is to certify that I, {doctor_name}, {doctor_qualification}{', Registration No: ' + doctor_reg_no if doctor_reg_no else ''}, "
                        f"have examined {patient_name}, {patient_gender}, Age: {patient_age} years, "
                        f"{patient_designation if patient_designation else 'Patient'} "
                        f"{('of ' + patient_office) if patient_office else ''} "
                        f"on {exam_date.strftime('%d/%m/%Y')}.")
    
    pdf.ln(5)
    pdf.multi_cell(0, 6, f"After careful examination, I hereby certify that the patient is suffering from {medical_condition}.")
    
    pdf.ln(5)
    leave_days = (leave_to - leave_from).days + 1
    pdf.multi_cell(0, 6, f"I consider that a period of absence from duty from {leave_from.strftime('%d/%m/%Y')} "
                        f"to {leave_to.strftime('%d/%m/%Y')} ({leave_days} day(s)) is absolutely necessary "
                        f"for the restoration of his/her health.")
    
    if notes:
        pdf.ln(5)
        pdf.multi_cell(0, 6, f"Additional Recommendations: {notes}")
    
    # Add signature section
    pdf.add_signature_section(doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='certificates')
    temp_path = temp_file.name
    pdf.output(temp_path)
    
    return temp_path

def generate_fitness_certificate(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                                 doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                                 applicant_name, applicant_age, applicant_gender, applicant_designation,
                                 applicant_office, exam_date, fitness_purpose, previous_illness, remarks):
    
    pdf = MedicalPDF()
    pdf.add_page()
    
    # Add clinic header
    pdf.add_clinic_header(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FITNESS CERTIFICATE", 0, 1, "C")
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date: {exam_date.strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 8, f"Certificate No: FC/{datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1)
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, f"This is to certify that I, {doctor_name}, {doctor_qualification}"
                        f"{', Registration No: ' + doctor_reg_no if doctor_reg_no else ''}, have carefully examined "
                        f"{applicant_name}, {applicant_gender}, Age: {applicant_age} years, "
                        f"{applicant_designation if applicant_designation else 'Applicant'} "
                        f"{('of ' + applicant_office) if applicant_office else ''} "
                        f"on {exam_date.strftime('%d/%m/%Y')}.")
    
    pdf.ln(5)
    pdf.multi_cell(0, 6, f"Purpose: {fitness_purpose}")
    
    if previous_illness:
        pdf.ln(3)
        pdf.multi_cell(0, 6, f"Previous Medical History: {previous_illness}")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.multi_cell(0, 6, "CERTIFICATION:")
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, remarks)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.multi_cell(0, 6, "The applicant is MEDICALLY FIT for the above-mentioned purpose.")
    
    # Add signature section
    pdf.add_signature_section(doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='certificates')
    temp_path = temp_file.name
    pdf.output(temp_path)
    
    return temp_path

def generate_sick_leave_certificate(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                                    doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                                    employee_name, employee_id, employee_dept, employee_company,
                                    exam_date, illness, leave_from, leave_to, rest_advised, follow_up):
    
    pdf = MedicalPDF()
    pdf.add_page()
    
    # Add clinic header
    pdf.add_clinic_header(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SICK LEAVE CERTIFICATE", 0, 1, "C")
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date: {exam_date.strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(3)
    
    pdf.cell(0, 6, "To,", 0, 1)
    pdf.cell(0, 6, "The HR Manager / Concerned Authority", 0, 1)
    pdf.cell(0, 6, employee_company, 0, 1)
    pdf.ln(5)
    
    pdf.cell(0, 6, f"Subject: Medical Certificate for Sick Leave", 0, 1)
    pdf.ln(3)
    
    pdf.cell(0, 6, "Dear Sir/Madam,", 0, 1)
    pdf.ln(3)
    
    pdf.multi_cell(0, 6, f"This is to certify that {employee_name}"
                        f"{', Employee ID: ' + employee_id if employee_id else ''}"
                        f"{', ' + employee_dept if employee_dept else ''} "
                        f"has been under my medical care.")
    
    pdf.ln(3)
    pdf.multi_cell(0, 6, f"After thorough examination on {exam_date.strftime('%d/%m/%Y')}, "
                        f"I have diagnosed the patient with {illness}.")
    
    pdf.ln(3)
    leave_days = (leave_to - leave_from).days + 1
    pdf.multi_cell(0, 6, f"Due to this medical condition, I recommend sick leave from "
                        f"{leave_from.strftime('%d/%m/%Y')} to {leave_to.strftime('%d/%m/%Y')} "
                        f"({leave_days} day(s)).")
    
    if rest_advised:
        pdf.ln(3)
        pdf.multi_cell(0, 6, "Complete bed rest and avoiding strenuous activities is advised during this period.")
    
    if follow_up:
        pdf.ln(3)
        pdf.multi_cell(0, 6, f"Follow-up consultation is scheduled for: {follow_up}")
    
    pdf.ln(5)
    pdf.multi_cell(0, 6, "I request you to kindly grant the necessary leave for the recovery and restoration of health.")
    
    pdf.ln(10)
    pdf.cell(0, 6, "Thanking you,", 0, 1)
    pdf.ln(10)
    
    # Add signature section
    pdf.add_signature_section(doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='certificates')
    temp_path = temp_file.name
    pdf.output(temp_path)
    
    return temp_path

def generate_form_1a(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                    doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                    applicant_name, applicant_age, applicant_gender, applicant_address,
                    license_type, exam_date, height, weight, vision_right, vision_left,
                    color_blind, hearing_normal, physical_deformity, fit_to_drive):
    
    pdf = MedicalPDF()
    pdf.add_page()
    
    # Add clinic header
    pdf.add_clinic_header(clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FORM 1A", 0, 1, "C")
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Medical Certificate for Driving License", 0, 1, "C")
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Date of Examination: {exam_date.strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(3)
    
    # Applicant Details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "APPLICANT DETAILS:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Name: {applicant_name}", 0, 1)
    pdf.cell(0, 6, f"Age: {applicant_age} years", 0, 1)
    pdf.cell(0, 6, f"Gender: {applicant_gender}", 0, 1)
    pdf.multi_cell(0, 6, f"Address: {applicant_address}")
    pdf.cell(0, 6, f"License Type Applied: {license_type}", 0, 1)
    pdf.ln(5)
    
    # Medical Examination
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "MEDICAL EXAMINATION REPORT:", 0, 1)
    pdf.set_font("Arial", "", 11)
    
    # Physical Measurements
    pdf.cell(0, 6, f"Height: {height} cm", 0, 1)
    pdf.cell(0, 6, f"Weight: {weight} kg", 0, 1)
    pdf.ln(2)
    
    # Vision Test
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Vision Test:", 0, 1)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"   Right Eye: {vision_right}", 0, 1)
    pdf.cell(0, 6, f"   Left Eye: {vision_left}", 0, 1)
    pdf.cell(0, 6, f"   Color Blindness: {'Yes' if color_blind else 'No'}", 0, 1)
    pdf.ln(2)
    
    # Other Tests
    pdf.cell(0, 6, f"Hearing: {'Normal' if hearing_normal else 'Impaired'}", 0, 1)
    if physical_deformity:
        pdf.multi_cell(0, 6, f"Physical Deformity: {physical_deformity}")
    else:
        pdf.cell(0, 6, "Physical Deformity: None", 0, 1)
    pdf.ln(5)
    
    # Certificate
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "CERTIFICATION:", 0, 1)
    pdf.set_font("Arial", "", 11)
    
    if fit_to_drive:
        pdf.multi_cell(0, 6, f"I, {doctor_name}, {doctor_qualification}{', Registration No: ' + doctor_reg_no if doctor_reg_no else ''}, "
                            f"hereby certify that I have personally examined the above-named applicant and "
                            f"find him/her MEDICALLY FIT to drive a {license_type}.")
    else:
        pdf.multi_cell(0, 6, f"I, {doctor_name}, {doctor_qualification}{', Registration No: ' + doctor_reg_no if doctor_reg_no else ''}, "
                            f"hereby certify that I have personally examined the above-named applicant and "
                            f"find him/her NOT FIT to drive at this time due to medical reasons.")
    
    pdf.ln(5)
    pdf.multi_cell(0, 6, "The applicant has been examined for any physical or mental disability that may "
                        "interfere with safe driving.")
    
    # Add signature section
    pdf.add_signature_section(doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir='certificates')
    temp_path = temp_file.name
    pdf.output(temp_path)
    
    return temp_path

# Main App UI
st.markdown('<div class="main-header"><h1>🏥 Medical Certificate Generator</h1><p>Professional Medical & Fitness Certificates</p></div>', unsafe_allow_html=True)

# Sidebar for clinic information
with st.sidebar:
    st.header("🏥 Clinic Information")
    clinic_name = st.text_input("Clinic Name", value="Medical Certificate Clinic")
    clinic_address = st.text_area("Clinic Address", value="123 Medical Street\nCity, State - 123456")
    clinic_phone = st.text_input("Contact Number", value="+91 1234567890")
    clinic_email = st.text_input("Email", value="clinic@medicalcert.in")
    clinic_reg = st.text_input("Registration Number", value="REG/2024/12345")
    
    st.divider()
    st.header("👨‍⚕️ Doctor Details")
    doctor_name = st.text_input("Doctor Name*", value="Dr. ")
    doctor_qualification = st.text_input("Qualification*", value="MBBS, MD")
    doctor_reg_no = st.text_input("Medical Registration No.*", value="MCI12345")
    doctor_specialty = st.text_input("Specialization", value="General Physician")
    
    st.divider()
    st.info("**Note:** All fields marked with * are required. Certificates include automatic stamp and signature section.")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📋 Medical Certificate", "💪 Fitness Certificate", "🏃 Sick Leave Certificate", "📄 Form 1A (RTO)"])

# Medical Certificate Tab
with tab1:
    st.markdown('<div class="cert-type-box"><h3>Medical Certificate</h3><p>For general medical purposes and sick leave</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Information")
        patient_name_mc = st.text_input("Patient Name*", key="patient_mc")
        patient_age_mc = st.number_input("Age", min_value=0, max_value=120, value=25, key="age_mc")
        patient_gender_mc = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender_mc")
        patient_designation_mc = st.text_input("Designation/Occupation", key="desig_mc")
        patient_office_mc = st.text_input("Office/Organization", key="office_mc")
        
    with col2:
        st.subheader("Medical Details")
        examination_date_mc = st.date_input("Date of Examination", value=date.today(), key="exam_date_mc")
        medical_condition = st.text_area("Medical Condition/Diagnosis*", 
                                        placeholder="E.g., Viral Fever, Acute Gastroenteritis", 
                                        key="condition_mc")
        
        col_from, col_to = st.columns(2)
        with col_from:
            leave_from_mc = st.date_input("Leave From*", value=date.today(), key="from_mc")
        with col_to:
            leave_to_mc = st.date_input("Leave To*", value=date.today(), key="to_mc")
        
        if leave_from_mc > leave_to_mc:
            st.error("⚠️ Leave 'From' date cannot be after 'To' date!")
        
        additional_notes_mc = st.text_area("Additional Recommendations", 
                                          placeholder="E.g., Complete bed rest advised", 
                                          key="notes_mc")
    
    if st.button("Generate Medical Certificate", key="gen_mc", type="primary"):
        if not all([patient_name_mc, medical_condition, doctor_name, doctor_qualification]):
            st.error("❌ Please fill all required fields marked with *")
        elif leave_from_mc > leave_to_mc:
            st.error("❌ Please correct the leave dates!")
        else:
            with st.spinner("Generating certificate..."):
                try:
                    pdf_path = generate_medical_certificate(
                        clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                        doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                        patient_name_mc, patient_age_mc, patient_gender_mc, patient_designation_mc,
                        patient_office_mc, examination_date_mc, medical_condition, 
                        leave_from_mc, leave_to_mc, additional_notes_mc
                    )
                    
                    # Read the generated PDF
                    with open(pdf_path, "rb") as file:
                        pdf_bytes = file.read()
                    
                    # Show success message and download button
                    st.success("✅ Medical Certificate Generated Successfully!")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Medical_Certificate_{patient_name_mc.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key="download_mc"
                        )
                    
                    # Preview PDF
                    with col_d2:
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"❌ Error generating certificate: {str(e)}")

# Fitness Certificate Tab
with tab2:
    st.markdown('<div class="cert-type-box"><h3>Fitness Certificate</h3><p>For employment, government service, and job applications</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Applicant Information")
        applicant_name_fc = st.text_input("Applicant Name*", key="applicant_fc")
        applicant_age_fc = st.number_input("Age", min_value=0, max_value=120, value=25, key="age_fc")
        applicant_gender_fc = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender_fc")
        applicant_designation_fc = st.text_input("Designation/Position Applied", key="desig_fc")
        applicant_office_fc = st.text_input("Office/Organization", key="office_fc")
        
    with col2:
        st.subheader("Fitness Details")
        examination_date_fc = st.date_input("Date of Examination", value=date.today(), key="exam_date_fc")
        fitness_purpose = st.selectbox("Purpose of Fitness Certificate", 
                                      ["Government Service", "Private Job", "Promotion", 
                                       "Transfer", "Sports/Athletics", "Other"], 
                                      key="purpose_fc")
        previous_illness = st.text_area("Previous Medical History (if any)", 
                                       placeholder="E.g., Recovered from fever", 
                                       key="prev_illness_fc")
        fitness_remarks = st.text_area("Medical Remarks", 
                                      value="The applicant is medically fit and has no physical disabilities that would prevent them from performing their duties.",
                                      key="remarks_fc")
    
    if st.button("Generate Fitness Certificate", key="gen_fc", type="primary"):
        if not all([applicant_name_fc, doctor_name, doctor_qualification]):
            st.error("❌ Please fill all required fields marked with *")
        else:
            with st.spinner("Generating certificate..."):
                try:
                    pdf_path = generate_fitness_certificate(
                        clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                        doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                        applicant_name_fc, applicant_age_fc, applicant_gender_fc, 
                        applicant_designation_fc, applicant_office_fc, examination_date_fc,
                        fitness_purpose, previous_illness, fitness_remarks
                    )
                    
                    with open(pdf_path, "rb") as file:
                        pdf_bytes = file.read()
                    
                    st.success("✅ Fitness Certificate Generated Successfully!")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Fitness_Certificate_{applicant_name_fc.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key="download_fc"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error generating certificate: {str(e)}")

# Sick Leave Certificate Tab
with tab3:
    st.markdown('<div class="cert-type-box"><h3>Sick Leave Certificate</h3><p>For employee sick leave documentation</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Employee Information")
        employee_name_sl = st.text_input("Employee Name*", key="employee_sl")
        employee_id = st.text_input("Employee ID", key="emp_id_sl")
        employee_dept = st.text_input("Department", key="dept_sl")
        employee_company = st.text_input("Company/Organization*", key="company_sl")
        
    with col2:
        st.subheader("Leave Details")
        examination_date_sl = st.date_input("Date of Examination", value=date.today(), key="exam_date_sl")
        illness_sl = st.text_area("Illness/Condition*", 
                                  placeholder="E.g., Acute Upper Respiratory Tract Infection", 
                                  key="illness_sl")
        
        col_from_sl, col_to_sl = st.columns(2)
        with col_from_sl:
            leave_from_sl = st.date_input("Leave From*", value=date.today(), key="from_sl")
        with col_to_sl:
            leave_to_sl = st.date_input("Leave To*", value=date.today(), key="to_sl")
        
        if leave_from_sl > leave_to_sl:
            st.error("⚠️ Leave 'From' date cannot be after 'To' date!")
        
        rest_advised = st.checkbox("Complete bed rest advised", value=True, key="rest_sl")
        follow_up = st.date_input("Follow-up Date (if applicable)", key="followup_sl")
    
    if st.button("Generate Sick Leave Certificate", key="gen_sl", type="primary"):
        if not all([employee_name_sl, employee_company, illness_sl, doctor_name, doctor_qualification]):
            st.error("❌ Please fill all required fields marked with *")
        elif leave_from_sl > leave_to_sl:
            st.error("❌ Please correct the leave dates!")
        else:
            with st.spinner("Generating certificate..."):
                try:
                    pdf_path = generate_sick_leave_certificate(
                        clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                        doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                        employee_name_sl, employee_id, employee_dept, employee_company,
                        examination_date_sl, illness_sl, leave_from_sl, leave_to_sl,
                        rest_advised, follow_up.strftime('%d/%m/%Y') if follow_up else None
                    )
                    
                    with open(pdf_path, "rb") as file:
                        pdf_bytes = file.read()
                    
                    st.success("✅ Sick Leave Certificate Generated Successfully!")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Sick_Leave_Certificate_{employee_name_sl.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key="download_sl"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error generating certificate: {str(e)}")

# Form 1A (RTO) Tab
with tab4:
    st.markdown('<div class="cert-type-box"><h3>Form 1A - Medical Certificate for Driving License</h3><p>For RTO Bangalore and other transport authorities</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Applicant Information")
        applicant_name_rto = st.text_input("Applicant Name*", key="applicant_rto")
        applicant_age_rto = st.number_input("Age", min_value=16, max_value=120, value=25, key="age_rto")
        applicant_gender_rto = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender_rto")
        applicant_address_rto = st.text_area("Address*", key="address_rto")
        license_type = st.selectbox("License Type*", 
                                   ["Two Wheeler", "Four Wheeler (LMV)", "Transport Vehicle", 
                                    "Commercial Vehicle", "Renewal"], 
                                   key="license_type")
        
    with col2:
        st.subheader("Medical Examination")
        examination_date_rto = st.date_input("Date of Examination", value=date.today(), key="exam_date_rto")
        
        st.write("**Physical Fitness**")
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170, key="height_rto")
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, key="weight_rto")
        
        st.write("**Vision Test**")
        vision_right = st.selectbox("Right Eye", ["6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60"], key="vision_r")
        vision_left = st.selectbox("Left Eye", ["6/6", "6/9", "6/12", "6/18", "6/24", "6/36", "6/60"], key="vision_l")
        color_blind = st.checkbox("Color Blindness Detected", key="color_blind")
        
        st.write("**Other Checks**")
        hearing_normal = st.checkbox("Hearing Normal", value=True, key="hearing")
        physical_deformity = st.text_input("Physical Deformity (if any)", key="deformity")
        fit_to_drive = st.checkbox("Fit to Drive", value=True, key="fit_drive")
    
    if st.button("Generate Form 1A", key="gen_rto", type="primary"):
        if not all([applicant_name_rto, applicant_address_rto, license_type, doctor_name, doctor_qualification]):
            st.error("❌ Please fill all required fields marked with *")
        else:
            with st.spinner("Generating certificate..."):
                try:
                    pdf_path = generate_form_1a(
                        clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg,
                        doctor_name, doctor_qualification, doctor_reg_no, doctor_specialty,
                        applicant_name_rto, applicant_age_rto, applicant_gender_rto,
                        applicant_address_rto, license_type, examination_date_rto,
                        height, weight, vision_right, vision_left, color_blind,
                        hearing_normal, physical_deformity, fit_to_drive
                    )
                    
                    with open(pdf_path, "rb") as file:
                        pdf_bytes = file.read()
                    
                    st.success("✅ Form 1A Generated Successfully!")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"Form_1A_{applicant_name_rto.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key="download_rto"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error generating certificate: {str(e)}")

# Footer
st.markdown("""
    <div class="footer">
        <p>🏥 <strong>Medical Certificate Generator</strong> | Professional Medical Documentation System</p>
        <p style='font-size: 12px; color: #666;'>⚠️ All certificates require doctor's signature and official seal to be valid</p>
        <p style='font-size: 12px; color: #666;'>📧 For support: clinic@medicalcert.in | 📞 +91 1234567890</p>
        <p style='font-size: 10px; color: #999;'>© 2024 Medical Certificate Generator. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

# Clean up old temporary files
def cleanup_old_files():
    """Clean up old temporary files"""
    import glob
    import time
    try:
        files = glob.glob("certificates/*.pdf")
        current_time = time.time()
        for file in files:
            file_time = os.path.getmtime(file)
            # Delete files older than 1 hour
            if current_time - file_time > 3600:
                os.remove(file)
    except:
        pass

# Run cleanup
cleanup_old_files()
