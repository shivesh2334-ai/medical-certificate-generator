from flask import Flask, request, send_file, render_template_string, jsonify
from datetime import datetime, date
from fpdf import FPDF
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)

# Create necessary directories
Path("certificates").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

# Function to create stamp image
def create_stamp_image():
    stamp_path = "static/stamp.png"
    if not os.path.exists(stamp_path):
        try:
            width, height = 300, 120
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            draw.rectangle([(0, 0), (width-1, height-1)], 
                         outline=(200, 0, 0, 255), width=2)
            draw.rectangle([(10, 10), (width-11, height-11)], 
                         outline=(200, 0, 0, 255), width=1)
            
            try:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            draw.text((width/2, 30), "MEDICAL STAMP", 
                     fill=(200, 0, 0, 255), font=font_large, anchor="mm")
            draw.text((width/2, 60), "Authorized Signatory", 
                     fill=(150, 0, 0, 255), font=font_small, anchor="mm")
            draw.text((width/2, 85), "Clinic Seal", 
                     fill=(150, 0, 0, 255), font=font_small, anchor="mm")
            
            image.save(stamp_path, "PNG")
        except Exception as e:
            print(f"Could not create stamp image: {str(e)}")
    return True

create_stamp_image()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Certificate Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .col {
            flex: 1;
        }
        .cert-type {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 5px solid #667eea;
            margin-bottom: 20px;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
        .btn:hover {
            background: #764ba2;
        }
        .tab-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
        }
        .tab.active {
            border-bottom: 3px solid #667eea;
            font-weight: bold;
        }
        .form-section {
            display: none;
        }
        .form-section.active {
            display: block;
        }
        .required::after {
            content: " *";
            color: red;
        }
        .message {
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Medical Certificate Generator</h1>
            <p>Professional Medical & Fitness Certificates</p>
        </div>
        
        <div class="tab-container">
            <button class="tab active" onclick="showTab(1)">Medical Certificate</button>
            <button class="tab" onclick="showTab(2)">Fitness Certificate</button>
            <button class="tab" onclick="showTab(3)">Sick Leave Certificate</button>
            <button class="tab" onclick="showTab(4)">Form 1A (RTO)</button>
        </div>
        
        <!-- Sidebar for Clinic Info -->
        <div class="row">
            <div class="col">
                <div class="cert-type">
                    <h3>🏥 Clinic Information</h3>
                    <div class="form-group">
                        <label class="required">Clinic Name</label>
                        <input type="text" id="clinic_name" value="Medical Certificate Clinic">
                    </div>
                    <div class="form-group">
                        <label class="required">Clinic Address</label>
                        <textarea id="clinic_address">123 Medical Street\nCity, State - 123456</textarea>
                    </div>
                    <div class="form-group">
                        <label class="required">Contact Number</label>
                        <input type="text" id="clinic_phone" value="+91 1234567890">
                    </div>
                    <div class="form-group">
                        <label>Registration Number</label>
                        <input type="text" id="clinic_reg" value="REG/2024/12345">
                    </div>
                    
                    <h3>👨‍⚕️ Doctor Details</h3>
                    <div class="form-group">
                        <label class="required">Doctor Name</label>
                        <input type="text" id="doctor_name" value="Dr. ">
                    </div>
                    <div class="form-group">
                        <label class="required">Qualification</label>
                        <input type="text" id="doctor_qualification" value="MBBS, MD">
                    </div>
                    <div class="form-group">
                        <label>Medical Registration No.</label>
                        <input type="text" id="doctor_reg_no" value="MCI12345">
                    </div>
                    <div class="form-group">
                        <label>Specialization</label>
                        <input type="text" id="doctor_specialty" value="General Physician">
                    </div>
                </div>
            </div>
            
            <!-- Forms -->
            <div class="col">
                <!-- Tab 1: Medical Certificate -->
                <div id="tab1" class="form-section active">
                    <div class="cert-type">
                        <h3>📋 Medical Certificate</h3>
                        <p>For general medical purposes and sick leave</p>
                    </div>
                    
                    <div class="row">
                        <div class="col">
                            <h4>Patient Information</h4>
                            <div class="form-group">
                                <label class="required">Patient Name</label>
                                <input type="text" id="patient_name">
                            </div>
                            <div class="form-group">
                                <label>Age</label>
                                <input type="number" id="patient_age" value="25">
                            </div>
                            <div class="form-group">
                                <label>Gender</label>
                                <select id="patient_gender">
                                    <option>Male</option>
                                    <option>Female</option>
                                    <option>Other</option>
                                </select>
                            </div>
                        </div>
                        <div class="col">
                            <h4>Medical Details</h4>
                            <div class="form-group">
                                <label class="required">Medical Condition/Diagnosis</label>
                                <textarea id="medical_condition" placeholder="E.g., Viral Fever, Acute Gastroenteritis"></textarea>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <div class="form-group">
                                        <label class="required">Leave From</label>
                                        <input type="date" id="leave_from" value="{{ today }}">
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="form-group">
                                        <label class="required">Leave To</label>
                                        <input type="date" id="leave_to" value="{{ today }}">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button class="btn" onclick="generateCertificate(1)">Generate Medical Certificate</button>
                </div>
                
                <!-- Tab 2: Fitness Certificate -->
                <div id="tab2" class="form-section">
                    <div class="cert-type">
                        <h3>💪 Fitness Certificate</h3>
                        <p>For employment, government service, and job applications</p>
                    </div>
                    
                    <div class="row">
                        <div class="col">
                            <h4>Applicant Information</h4>
                            <div class="form-group">
                                <label class="required">Applicant Name</label>
                                <input type="text" id="applicant_name_fc">
                            </div>
                            <div class="form-group">
                                <label>Age</label>
                                <input type="number" id="applicant_age_fc" value="25">
                            </div>
                            <div class="form-group">
                                <label>Gender</label>
                                <select id="applicant_gender_fc">
                                    <option>Male</option>
                                    <option>Female</option>
                                    <option>Other</option>
                                </select>
                            </div>
                        </div>
                        <div class="col">
                            <h4>Fitness Details</h4>
                            <div class="form-group">
                                <label>Purpose</label>
                                <select id="fitness_purpose">
                                    <option>Government Service</option>
                                    <option>Private Job</option>
                                    <option>Promotion</option>
                                    <option>Transfer</option>
                                    <option>Sports/Athletics</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Medical Remarks</label>
                                <textarea id="fitness_remarks">The applicant is medically fit and has no physical disabilities that would prevent them from performing their duties.</textarea>
                            </div>
                        </div>
                    </div>
                    <button class="btn" onclick="generateCertificate(2)">Generate Fitness Certificate</button>
                </div>
                
                <!-- Tab 3: Sick Leave Certificate -->
                <div id="tab3" class="form-section">
                    <div class="cert-type">
                        <h3>🏃 Sick Leave Certificate</h3>
                        <p>For employee sick leave documentation</p>
                    </div>
                    
                    <div class="row">
                        <div class="col">
                            <h4>Employee Information</h4>
                            <div class="form-group">
                                <label class="required">Employee Name</label>
                                <input type="text" id="employee_name_sl">
                            </div>
                            <div class="form-group">
                                <label class="required">Company/Organization</label>
                                <input type="text" id="employee_company">
                            </div>
                        </div>
                        <div class="col">
                            <h4>Leave Details</h4>
                            <div class="form-group">
                                <label class="required">Illness/Condition</label>
                                <textarea id="illness_sl" placeholder="E.g., Acute Upper Respiratory Tract Infection"></textarea>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <div class="form-group">
                                        <label class="required">Leave From</label>
                                        <input type="date" id="leave_from_sl" value="{{ today }}">
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="form-group">
                                        <label class="required">Leave To</label>
                                        <input type="date" id="leave_to_sl" value="{{ today }}">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button class="btn" onclick="generateCertificate(3)">Generate Sick Leave Certificate</button>
                </div>
                
                <!-- Tab 4: Form 1A -->
                <div id="tab4" class="form-section">
                    <div class="cert-type">
                        <h3>📄 Form 1A (RTO)</h3>
                        <p>Medical Certificate for Driving License</p>
                    </div>
                    
                    <div class="row">
                        <div class="col">
                            <h4>Applicant Information</h4>
                            <div class="form-group">
                                <label class="required">Applicant Name</label>
                                <input type="text" id="applicant_name_rto">
                            </div>
                            <div class="form-group">
                                <label class="required">Address</label>
                                <textarea id="applicant_address_rto"></textarea>
                            </div>
                            <div class="form-group">
                                <label class="required">License Type</label>
                                <select id="license_type">
                                    <option>Two Wheeler</option>
                                    <option>Four Wheeler (LMV)</option>
                                    <option>Transport Vehicle</option>
                                    <option>Commercial Vehicle</option>
                                    <option>Renewal</option>
                                </select>
                            </div>
                        </div>
                        <div class="col">
                            <h4>Medical Examination</h4>
                            <div class="row">
                                <div class="col">
                                    <div class="form-group">
                                        <label>Height (cm)</label>
                                        <input type="number" id="height" value="170">
                                    </div>
                                </div>
                                <div class="col">
                                    <div class="form-group">
                                        <label>Weight (kg)</label>
                                        <input type="number" id="weight" value="70">
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Vision - Right Eye</label>
                                <select id="vision_right">
                                    <option>6/6</option>
                                    <option>6/9</option>
                                    <option>6/12</option>
                                    <option>6/18</option>
                                    <option>6/24</option>
                                    <option>6/36</option>
                                    <option>6/60</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Vision - Left Eye</label>
                                <select id="vision_left">
                                    <option>6/6</option>
                                    <option>6/9</option>
                                    <option>6/12</option>
                                    <option>6/18</option>
                                    <option>6/24</option>
                                    <option>6/36</option>
                                    <option>6/60</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <button class="btn" onclick="generateCertificate(4)">Generate Form 1A</button>
                </div>
                
                <!-- Message Area -->
                <div id="message" class="message"></div>
                
                <!-- Download Link -->
                <div id="downloadSection" style="display: none; margin-top: 20px;">
                    <h3>✅ Certificate Generated Successfully!</h3>
                    <a id="downloadLink" class="btn" style="background: #28a745;" download>📥 Download PDF</a>
                </div>
            </div>
        </div>
        
        <div class="footer" style="margin-top: 40px; text-align: center; color: #666; border-top: 1px solid #eee; padding-top: 20px;">
            <p>🏥 <strong>Medical Certificate Generator</strong> | Professional Medical Documentation System</p>
            <p style="font-size: 12px;">⚠️ All certificates require doctor's signature and official seal to be valid</p>
        </div>
    </div>
    
    <script>
        let currentTab = 1;
        
        function showTab(tabNumber) {
            // Hide all tabs
            document.querySelectorAll('.form-section').forEach(section => {
                section.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById('tab' + tabNumber).classList.add('active');
            document.querySelectorAll('.tab')[tabNumber - 1].classList.add('active');
            currentTab = tabNumber;
            
            // Hide download section
            document.getElementById('downloadSection').style.display = 'none';
            document.getElementById('message').style.display = 'none';
        }
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = 'message ' + type;
            messageDiv.style.display = 'block';
            
            // Scroll to message
            messageDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function generateCertificate(type) {
            // Collect data based on type
            const data = {
                clinic_name: document.getElementById('clinic_name').value,
                clinic_address: document.getElementById('clinic_address').value,
                clinic_phone: document.getElementById('clinic_phone').value,
                clinic_reg: document.getElementById('clinic_reg').value,
                doctor_name: document.getElementById('doctor_name').value,
                doctor_qualification: document.getElementById('doctor_qualification').value,
                doctor_reg_no: document.getElementById('doctor_reg_no').value,
                doctor_specialty: document.getElementById('doctor_specialty').value,
                certificate_type: type,
                today: new Date().toISOString().split('T')[0]
            };
            
            // Add specific data based on certificate type
            if (type === 1) { // Medical Certificate
                data.patient_name = document.getElementById('patient_name').value;
                data.patient_age = document.getElementById('patient_age').value;
                data.patient_gender = document.getElementById('patient_gender').value;
                data.medical_condition = document.getElementById('medical_condition').value;
                data.leave_from = document.getElementById('leave_from').value;
                data.leave_to = document.getElementById('leave_to').value;
                
                if (!data.patient_name || !data.medical_condition || !data.doctor_name || !data.doctor_qualification) {
                    showMessage('Please fill all required fields marked with *', 'error');
                    return;
                }
                
            } else if (type === 2) { // Fitness Certificate
                data.applicant_name = document.getElementById('applicant_name_fc').value;
                data.applicant_age = document.getElementById('applicant_age_fc').value;
                data.applicant_gender = document.getElementById('applicant_gender_fc').value;
                data.fitness_purpose = document.getElementById('fitness_purpose').value;
                data.fitness_remarks = document.getElementById('fitness_remarks').value;
                
                if (!data.applicant_name || !data.doctor_name || !data.doctor_qualification) {
                    showMessage('Please fill all required fields marked with *', 'error');
                    return;
                }
                
            } else if (type === 3) { // Sick Leave Certificate
                data.employee_name = document.getElementById('employee_name_sl').value;
                data.employee_company = document.getElementById('employee_company').value;
                data.illness = document.getElementById('illness_sl').value;
                data.leave_from = document.getElementById('leave_from_sl').value;
                data.leave_to = document.getElementById('leave_to_sl').value;
                
                if (!data.employee_name || !data.employee_company || !data.illness || !data.doctor_name || !data.doctor_qualification) {
                    showMessage('Please fill all required fields marked with *', 'error');
                    return;
                }
                
            } else if (type === 4) { // Form 1A
                data.applicant_name = document.getElementById('applicant_name_rto').value;
                data.applicant_address = document.getElementById('applicant_address_rto').value;
                data.license_type = document.getElementById('license_type').value;
                data.height = document.getElementById('height').value;
                data.weight = document.getElementById('weight').value;
                data.vision_right = document.getElementById('vision_right').value;
                data.vision_left = document.getElementById('vision_left').value;
                data.fit_to_drive = true;
                
                if (!data.applicant_name || !data.applicant_address || !data.license_type || !data.doctor_name || !data.doctor_qualification) {
                    showMessage('Please fill all required fields marked with *', 'error');
                    return;
                }
            }
            
            showMessage('Generating certificate... Please wait.', 'success');
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        const downloadLink = document.getElementById('downloadLink');
                        downloadLink.href = result.download_url;
                        downloadLink.download = result.filename;
                        
                        document.getElementById('downloadSection').style.display = 'block';
                        document.getElementById('message').style.display = 'none';
                        
                        // Scroll to download section
                        document.getElementById('downloadSection').scrollIntoView({ behavior: 'smooth' });
                    } else {
                        showMessage(result.error || 'Error generating certificate', 'error');
                    }
                } else {
                    showMessage('Error generating certificate', 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }
        
        // Set today's date for date inputs
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('leave_from').value = today;
            document.getElementById('leave_to').value = today;
            document.getElementById('leave_from_sl').value = today;
            document.getElementById('leave_to_sl').value = today;
        });
    </script>
</body>
</html>
"""

# PDF Generation Functions (same as before, but adapted for Flask)
class MedicalPDF(FPDF):
    def add_clinic_header(self, clinic_name, clinic_address, clinic_phone, clinic_email, clinic_reg):
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
        self.ln(15)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, "Place: _________________", 0, 1)
        self.cell(0, 6, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
        self.ln(10)
        
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, f"Dr. {doctor_name}", 0, 1, "R")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, doctor_qualification, 0, 1, "R")
        if doctor_reg_no:
            self.cell(0, 5, f"Reg. No: {doctor_reg_no}", 0, 1, "R")
        if doctor_specialty:
            self.cell(0, 5, doctor_specialty, 0, 1, "R")
        
        stamp_path = "static/stamp.png"
        if os.path.exists(stamp_path):
            try:
                stamp_x = (210 - 40) / 2
                stamp_y = self.get_y() + 5
                self.image(stamp_path, x=stamp_x, y=stamp_y, w=40)
                self.ln(25)
            except Exception as e:
                print(f"Error adding stamp: {e}")

@app.route('/')
def index():
    today = date.today().isoformat()
    return render_template_string(HTML_TEMPLATE, today=today)

@app.route('/generate', methods=['POST'])
def generate_certificate():
    try:
        data = request.json
        
        # Create PDF based on certificate type
        if data['certificate_type'] == 1:  # Medical Certificate
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], data['clinic_address'], 
                data['clinic_phone'], "clinic@medicalcert.in", data['clinic_reg']
            )
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "MEDICAL CERTIFICATE", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.ln(3)
            
            leave_from = datetime.strptime(data['leave_from'], '%Y-%m-%d').date()
            leave_to = datetime.strptime(data['leave_to'], '%Y-%m-%d').date()
            leave_days = (leave_to - leave_from).days + 1
            
            pdf.multi_cell(0, 6, f"This is to certify that I, {data['doctor_name']}, {data['doctor_qualification']}, "
                               f"{'Registration No: ' + data['doctor_reg_no'] if data['doctor_reg_no'] else ''}, "
                               f"have examined {data['patient_name']}, {data['patient_gender']}, "
                               f"Age: {data['patient_age']} years on {datetime.now().strftime('%d/%m/%Y')}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"After careful examination, I hereby certify that the patient is suffering from {data['medical_condition']}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"I consider that a period of absence from duty from {leave_from.strftime('%d/%m/%Y')} "
                               f"to {leave_to.strftime('%d/%m/%Y')} ({leave_days} day(s)) is absolutely necessary "
                               f"for the restoration of his/her health.")
            
            pdf.add_signature_section(
                data['doctor_name'], data['doctor_qualification'],
                data['doctor_reg_no'], data['doctor_specialty']
            )
            
            filename = f"Medical_Certificate_{data['patient_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        elif data['certificate_type'] == 2:  # Fitness Certificate
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], data['clinic_address'], 
                data['clinic_phone'], "clinic@medicalcert.in", data['clinic_reg']
            )
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "FITNESS CERTIFICATE", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.cell(0, 8, f"Certificate No: FC/{datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1)
            pdf.ln(3)
            
            pdf.multi_cell(0, 6, f"This is to certify that I, {data['doctor_name']}, {data['doctor_qualification']}"
                               f"{', Registration No: ' + data['doctor_reg_no'] if data['doctor_reg_no'] else ''}, "
                               f"have carefully examined {data['applicant_name']}, {data['applicant_gender']}, "
                               f"Age: {data['applicant_age']} years on {datetime.now().strftime('%d/%m/%Y')}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"Purpose: {data['fitness_purpose']}")
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 6, "CERTIFICATION:")
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 6, data['fitness_remarks'])
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 6, "The applicant is MEDICALLY FIT for the above-mentioned purpose.")
            
            pdf.add_signature_section(
                data['doctor_name'], data['doctor_qualification'],
                data['doctor_reg_no'], data['doctor_specialty']
            )
            
            filename = f"Fitness_Certificate_{data['applicant_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        elif data['certificate_type'] == 3:  # Sick Leave Certificate
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], data['clinic_address'], 
                data['clinic_phone'], "clinic@medicalcert.in", data['clinic_reg']
            )
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SICK LEAVE CERTIFICATE", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.ln(3)
            
            pdf.cell(0, 6, "To,", 0, 1)
            pdf.cell(0, 6, "The HR Manager / Concerned Authority", 0, 1)
            pdf.cell(0, 6, data['employee_company'], 0, 1)
            pdf.ln(5)
            
            pdf.cell(0, 6, "Subject: Medical Certificate for Sick Leave", 0, 1)
            pdf.ln(3)
            
            pdf.cell(0, 6, "Dear Sir/Madam,", 0, 1)
            pdf.ln(3)
            
            leave_from = datetime.strptime(data['leave_from'], '%Y-%m-%d').date()
            leave_to = datetime.strptime(data['leave_to'], '%Y-%m-%d').date()
            leave_days = (leave_to - leave_from).days + 1
            
            pdf.multi_cell(0, 6, f"This is to certify that {data['employee_name']} has been under my medical care.")
            
            pdf.ln(3)
            pdf.multi_cell(0, 6, f"After thorough examination on {datetime.now().strftime('%d/%m/%Y')}, "
                               f"I have diagnosed the patient with {data['illness']}.")
            
            pdf.ln(3)
            pdf.multi_cell(0, 6, f"Due to this medical condition, I recommend sick leave from "
                               f"{leave_from.strftime('%d/%m/%Y')} to {leave_to.strftime('%d/%m/%Y')} "
                               f"({leave_days} day(s)).")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, "I request you to kindly grant the necessary leave for the recovery and restoration of health.")
            
            pdf.ln(10)
            pdf.cell(0, 6, "Thanking you,", 0, 1)
            pdf.ln(10)
            
            pdf.add_signature_section(
                data['doctor_name'], data['doctor_qualification'],
                data['doctor_reg_no'], data['doctor_specialty']
            )
            
            filename = f"Sick_Leave_Certificate_{data['employee_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        elif data['certificate_type'] == 4:  # Form 1A
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], data['clinic_address'], 
                data['clinic_phone'], "clinic@medicalcert.in", data['clinic_reg']
            )
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "FORM 1A", 0, 1, "C")
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 8, "Medical Certificate for Driving License", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Date of Examination: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.ln(3)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "APPLICANT DETAILS:", 0, 1)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 6, f"Name: {data['applicant_name']}", 0, 1)
            pdf.cell(0, 6, f"Age: {data.get('applicant_age', 'N/A')} years", 0, 1)
            pdf.multi_cell(0, 6, f"Address: {data['applicant_address']}")
            pdf.cell(0, 6, f"License Type Applied: {data['license_type']}", 0, 1)
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "MEDICAL EXAMINATION REPORT:", 0, 1)
            pdf.set_font("Arial", "", 11)
            
            pdf.cell(0, 6, f"Height: {data['height']} cm", 0, 1)
            pdf.cell(0, 6, f"Weight: {data['weight']} kg", 0, 1)
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 6, "Vision Test:", 0, 1)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 6, f"   Right Eye: {data['vision_right']}", 0, 1)
            pdf.cell(0, 6, f"   Left Eye: {data['vision_left']}", 0, 1)
            pdf.cell(0, 6, f"   Color Blindness: No", 0, 1)
            pdf.ln(2)
            
            pdf.cell(0, 6, f"Hearing: Normal", 0, 1)
            pdf.cell(0, 6, "Physical Deformity: None", 0, 1)
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "CERTIFICATION:", 0, 1)
            pdf.set_font("Arial", "", 11)
            
            pdf.multi_cell(0, 6, f"I, {data['doctor_name']}, {data['doctor_qualification']}"
                               f"{', Registration No: ' + data['doctor_reg_no'] if data['doctor_reg_no'] else ''}, "
                               f"hereby certify that I have personally examined the above-named applicant and "
                               f"find him/her MEDICALLY FIT to drive a {data['license_type']}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, "The applicant has been examined for any physical or mental disability that may "
                               "interfere with safe driving.")
            
            pdf.add_signature_section(
                data['doctor_name'], data['doctor_qualification'],
                data['doctor_reg_no'], data['doctor_specialty']
            )
            
            filename = f"Form_1A_{data['applicant_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Save PDF to bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        # Save to temporary file
        temp_dir = "certificates"
        Path(temp_dir).mkdir(exist_ok=True)
        temp_path = os.path.join(temp_dir, filename)
        
        with open(temp_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join("certificates", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

# Clean up old files periodically
import atexit
import glob
import time

def cleanup_files():
    try:
        files = glob.glob("certificates/*.pdf")
        current_time = time.time()
        for file in files:
            file_time = os.path.getmtime(file)
            if current_time - file_time > 3600:  # 1 hour
                os.remove(file)
    except:
        pass

atexit.register(cleanup_files)

if __name__ == '__main__':
    app.run(debug=True)
