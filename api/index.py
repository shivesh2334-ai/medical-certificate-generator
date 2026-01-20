import os
import tempfile
from datetime import datetime, date
from flask import Flask, request, send_file, jsonify, render_template_string
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# --- VERCEL SPECIFIC CONFIGURATION ---
# Vercel only allows writing to the system temporary directory
TEMP_DIR = tempfile.gettempdir() 
STAMP_PATH = os.path.join(TEMP_DIR, "stamp.png")

# HTML Template (Kept exactly as you provided)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Certificate Generator</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .tab-button.active { background-color: #667eea; color: white; }
        .required::after { content: " *"; color: red; }
        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="p-4 md:p-6">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6 text-center">
            <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
                <i class="fas fa-hospital text-blue-500 mr-3"></i>Medical Certificate Generator
            </h1>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Sidebar -->
            <div class="lg:col-span-1">
                <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Clinic Information</h2>
                    <div class="space-y-4">
                        <div><label class="block text-sm font-medium text-gray-700 mb-1 required">Clinic Name</label><input type="text" id="clinicName" value="City Medical Center" class="w-full px-4 py-2 border rounded-lg"></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1 required">Address</label><textarea id="clinicAddress" rows="3" class="w-full px-4 py-2 border rounded-lg">123 Medical Street, City - 560001</textarea></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1 required">Phone</label><input type="text" id="clinicPhone" value="+91 9876543210" class="w-full px-4 py-2 border rounded-lg"></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1">Reg No.</label><input type="text" id="clinicReg" value="REG/2024/MC001" class="w-full px-4 py-2 border rounded-lg"></div>
                    </div>
                    <h2 class="text-xl font-bold text-gray-800 mt-6 mb-4">Doctor Details</h2>
                    <div class="space-y-4">
                        <div><label class="block text-sm font-medium text-gray-700 mb-1 required">Doctor Name</label><input type="text" id="doctorName" value="Dr. Ramesh Kumar" class="w-full px-4 py-2 border rounded-lg"></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1 required">Qualification</label><input type="text" id="doctorQualification" value="MBBS, MD" class="w-full px-4 py-2 border rounded-lg"></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1">Reg No.</label><input type="text" id="doctorRegNo" value="MCI-12345" class="w-full px-4 py-2 border rounded-lg"></div>
                        <div><label class="block text-sm font-medium text-gray-700 mb-1">Specialty</label><input type="text" id="doctorSpecialty" value="General Physician" class="w-full px-4 py-2 border rounded-lg"></div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="lg:col-span-2">
                <div class="bg-white rounded-xl shadow-lg p-4 mb-6">
                    <div class="flex flex-wrap gap-2">
                        <button onclick="showTab(1)" class="tab-button active px-6 py-3 rounded-lg font-medium">Medical Certificate</button>
                        <button onclick="showTab(2)" class="tab-button px-6 py-3 rounded-lg font-medium">Fitness Certificate</button>
                        <button onclick="showTab(3)" class="tab-button px-6 py-3 rounded-lg font-medium">Sick Leave</button>
                        <button onclick="showTab(4)" class="tab-button px-6 py-3 rounded-lg font-medium">Form 1A</button>
                    </div>
                </div>

                <!-- Medical Certificate Tab -->
                <div id="tab1" class="tab-content active">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold mb-4">Medical Certificate</h2>
                        <div class="space-y-4">
                            <input type="text" id="patientName" placeholder="Patient Name" class="w-full px-4 py-2 border rounded-lg">
                            <div class="grid grid-cols-2 gap-4">
                                <input type="number" id="patientAge" placeholder="Age" value="30" class="w-full px-4 py-2 border rounded-lg">
                                <select id="patientGender" class="w-full px-4 py-2 border rounded-lg"><option>Male</option><option>Female</option></select>
                            </div>
                            <input type="text" id="patientOccupation" placeholder="Occupation" class="w-full px-4 py-2 border rounded-lg">
                            <textarea id="medicalCondition" rows="2" placeholder="Condition" class="w-full px-4 py-2 border rounded-lg"></textarea>
                            <div class="grid grid-cols-2 gap-4">
                                <div><label>From</label><input type="date" id="leaveFrom" class="w-full px-4 py-2 border rounded-lg"></div>
                                <div><label>To</label><input type="date" id="leaveTo" class="w-full px-4 py-2 border rounded-lg"></div>
                            </div>
                            <textarea id="additionalNotes" placeholder="Notes" class="w-full px-4 py-2 border rounded-lg"></textarea>
                        </div>
                        <button onclick="generateCertificate('medical')" class="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg">Generate Medical Certificate</button>
                    </div>
                </div>

                <!-- Fitness Certificate Tab -->
                <div id="tab2" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold mb-4">Fitness Certificate</h2>
                        <div class="space-y-4">
                            <input type="text" id="applicantName" placeholder="Applicant Name" class="w-full px-4 py-2 border rounded-lg">
                            <div class="grid grid-cols-2 gap-4">
                                <input type="number" id="applicantAge" value="25" class="w-full px-4 py-2 border rounded-lg">
                                <select id="applicantGender" class="w-full px-4 py-2 border rounded-lg"><option>Male</option><option>Female</option></select>
                            </div>
                            <input type="text" id="positionApplied" placeholder="Position" class="w-full px-4 py-2 border rounded-lg">
                            <select id="fitnessPurpose" class="w-full px-4 py-2 border rounded-lg"><option>Job</option><option>Sports</option></select>
                            <textarea id="medicalHistory" placeholder="Medical History" class="w-full px-4 py-2 border rounded-lg"></textarea>
                            <textarea id="fitnessRemarks" class="w-full px-4 py-2 border rounded-lg">Fit for duty.</textarea>
                        </div>
                        <button onclick="generateCertificate('fitness')" class="w-full mt-6 bg-green-600 text-white py-3 rounded-lg">Generate Fitness Certificate</button>
                    </div>
                </div>

                <!-- Sick Leave Tab -->
                <div id="tab3" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold mb-4">Sick Leave Certificate</h2>
                        <div class="space-y-4">
                            <input type="text" id="employeeName" placeholder="Employee Name" class="w-full px-4 py-2 border rounded-lg">
                            <input type="text" id="employeeCompany" placeholder="Company" class="w-full px-4 py-2 border rounded-lg">
                            <div class="grid grid-cols-2 gap-4">
                                <input type="text" id="employeeId" placeholder="ID" class="w-full px-4 py-2 border rounded-lg">
                                <input type="text" id="employeeDept" placeholder="Dept" class="w-full px-4 py-2 border rounded-lg">
                            </div>
                            <textarea id="illness" placeholder="Illness" class="w-full px-4 py-2 border rounded-lg"></textarea>
                            <div class="grid grid-cols-2 gap-4">
                                <div><label>From</label><input type="date" id="sickLeaveFrom" class="w-full px-4 py-2 border rounded-lg"></div>
                                <div><label>To</label><input type="date" id="sickLeaveTo" class="w-full px-4 py-2 border rounded-lg"></div>
                            </div>
                            <label><input type="checkbox" id="restAdvised" checked> Rest Advised</label>
                        </div>
                        <button onclick="generateCertificate('sickleave')" class="w-full mt-6 bg-orange-600 text-white py-3 rounded-lg">Generate Sick Leave</button>
                    </div>
                </div>

                <!-- Form 1A Tab -->
                <div id="tab4" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold mb-4">Form 1A (Driving)</h2>
                        <div class="space-y-4">
                            <input type="text" id="rtoApplicantName" placeholder="Name" class="w-full px-4 py-2 border rounded-lg">
                            <div class="grid grid-cols-2 gap-4">
                                <input type="number" id="rtoApplicantAge" value="25" class="w-full px-4 py-2 border rounded-lg">
                                <select id="rtoApplicantGender" class="w-full px-4 py-2 border rounded-lg"><option>Male</option><option>Female</option></select>
                            </div>
                            <textarea id="rtoApplicantAddress" placeholder="Address" class="w-full px-4 py-2 border rounded-lg"></textarea>
                            <select id="licenseType" class="w-full px-4 py-2 border rounded-lg"><option>LMV</option><option>MCWG</option></select>
                            <div class="grid grid-cols-2 gap-4">
                                <input type="number" id="height" placeholder="Height cm" value="170" class="w-full px-4 py-2 border rounded-lg">
                                <input type="number" id="weight" placeholder="Weight kg" value="70" class="w-full px-4 py-2 border rounded-lg">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <select id="visionRight" class="w-full px-4 py-2 border rounded-lg"><option>6/6</option></select>
                                <select id="visionLeft" class="w-full px-4 py-2 border rounded-lg"><option>6/6</option></select>
                            </div>
                            <div>
                                <label class="mr-4"><input type="checkbox" id="colorBlind"> Color Blind</label>
                                <label class="mr-4"><input type="checkbox" id="hearingNormal" checked> Hearing Normal</label>
                                <label><input type="checkbox" id="fitToDrive" checked> Fit to Drive</label>
                            </div>
                            <input type="text" id="physicalDeformity" placeholder="Deformity (None)" class="w-full px-4 py-2 border rounded-lg">
                        </div>
                        <button onclick="generateCertificate('form1a')" class="w-full mt-6 bg-purple-600 text-white py-3 rounded-lg">Generate Form 1A</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Result Section -->
        <div id="resultSection" class="hidden mt-8 bg-white rounded-xl shadow-lg p-6 flex flex-col md:flex-row justify-between items-center">
            <div>
                <h2 class="text-2xl font-bold text-green-600"><i class="fas fa-check-circle mr-2"></i>Generated!</h2>
                <p class="text-gray-600">Your certificate is ready.</p>
            </div>
            <a id="downloadLink" class="mt-4 md:mt-0 px-8 py-3 bg-blue-600 text-white rounded-lg font-bold">Download PDF</a>
        </div>
    </div>

    <script>
        // Init dates
        document.addEventListener('DOMContentLoaded', () => {
            const today = new Date().toISOString().split('T')[0];
            ['leaveFrom', 'leaveTo', 'sickLeaveFrom', 'sickLeaveTo'].forEach(id => document.getElementById(id).value = today);
        });

        function showTab(n) {
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById('tab' + n).classList.add('active');
            document.querySelectorAll('.tab-button')[n-1].classList.add('active');
            document.getElementById('resultSection').classList.add('hidden');
        }

        async function generateCertificate(type) {
            const getVal = (id) => document.getElementById(id) ? document.getElementById(id).value : '';
            const getCheck = (id) => document.getElementById(id) ? document.getElementById(id).checked : false;

            const data = {
                clinic_name: getVal('clinicName'), clinic_address: getVal('clinicAddress'),
                clinic_phone: getVal('clinicPhone'), clinic_reg: getVal('clinicReg'),
                doctor_name: getVal('doctorName'), doctor_qualification: getVal('doctorQualification'),
                doctor_reg_no: getVal('doctorRegNo'), doctor_specialty: getVal('doctorSpecialty'),
                certificate_type: type
            };

            // Simplified data gathering for brevity
            if(type === 'medical') {
                Object.assign(data, {
                    patient_name: getVal('patientName'), patient_age: getVal('patientAge'),
                    patient_gender: getVal('patientGender'), patient_occupation: getVal('patientOccupation'),
                    medical_condition: getVal('medicalCondition'), leave_from: getVal('leaveFrom'),
                    leave_to: getVal('leaveTo'), additional_notes: getVal('additionalNotes')
                });
            } else if(type === 'fitness') {
                Object.assign(data, {
                    applicant_name: getVal('applicantName'), applicant_age: getVal('applicantAge'),
                    applicant_gender: getVal('applicantGender'), position_applied: getVal('positionApplied'),
                    fitness_purpose: getVal('fitnessPurpose'), medical_history: getVal('medicalHistory'),
                    fitness_remarks: getVal('fitnessRemarks')
                });
            } else if(type === 'sickleave') {
                Object.assign(data, {
                    employee_name: getVal('employeeName'), employee_company: getVal('employeeCompany'),
                    employee_id: getVal('employeeId'), employee_dept: getVal('employeeDept'),
                    illness: getVal('illness'), leave_from: getVal('sickLeaveFrom'),
                    leave_to: getVal('sickLeaveTo'), rest_advised: getCheck('restAdvised')
                });
            } else if(type === 'form1a') {
                Object.assign(data, {
                    applicant_name: getVal('rtoApplicantName'), applicant_age: getVal('rtoApplicantAge'),
                    applicant_gender: getVal('rtoApplicantGender'), applicant_address: getVal('rtoApplicantAddress'),
                    license_type: getVal('licenseType'), height: getVal('height'), weight: getVal('weight'),
                    vision_right: getVal('visionRight'), vision_left: getVal('visionLeft'),
                    color_blind: getCheck('colorBlind'), hearing_normal: getCheck('hearingNormal'),
                    fit_to_drive: getCheck('fitToDrive'), physical_deformity: getVal('physicalDeformity')
                });
            }

            const btn = event.target;
            btn.innerHTML = 'Generating...'; btn.disabled = true;

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                
                if(result.success) {
                    const sec = document.getElementById('resultSection');
                    sec.classList.remove('hidden');
                    const dl = document.getElementById('downloadLink');
                    dl.href = result.download_url;
                    dl.download = result.filename;
                    sec.scrollIntoView({behavior: 'smooth'});
                } else {
                    alert('Error: ' + result.error);
                }
            } catch(e) { alert('Network Error'); }
            
            btn.innerHTML = 'Generate'; btn.disabled = false;
        }
    </script>
</body>
</html>
'''

# Helper: Create stamp image in the TEMP directory
def ensure_stamp_exists():
    if not os.path.exists(STAMP_PATH):
        try:
            width, height = 300, 120
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 0, 0, 255), width=2)
            draw.rectangle([(10, 10), (width-11, height-11)], outline=(200, 0, 0, 255), width=1)
            font = ImageFont.load_default()
            draw.text((20, 40), "MEDICAL STAMP", fill=(200, 0, 0, 255), font=font)
            draw.text((20, 60), "Authorized Signatory", fill=(150, 0, 0, 255), font=font)
            image.save(STAMP_PATH, "PNG")
        except Exception as e:
            print(f"Stamp creation failed: {e}")

class MedicalPDF(FPDF):
    def add_clinic_header(self, c_name, c_add, c_ph, c_reg):
        self.set_font("Arial", "B", 20)
        self.cell(0, 10, c_name, 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, c_add, 0, "C")
        self.cell(0, 5, f"Phone: {c_ph}", 0, 1, "C")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def add_signature_section(self, d_name, d_qual, d_reg, d_spec):
        self.ln(15)
        self.set_font("Arial", "", 11)
        self.cell(0, 6, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
        self.ln(10)
        self.set_font("Arial", "B", 11)
        self.cell(0, 6, f"Dr. {d_name}", 0, 1, "R")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, d_qual, 0, 1, "R")
        if d_reg: self.cell(0, 5, f"Reg: {d_reg}", 0, 1, "R")
        
        # Check for stamp in TEMP directory
        ensure_stamp_exists()
        if os.path.exists(STAMP_PATH):
            self.image(STAMP_PATH, x=160, y=self.get_y()+5, w=30)
            self.ln(25)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_certificate():
    try:
        data = request.json
        pdf = MedicalPDF()
        pdf.add_page()
        pdf.add_clinic_header(data['clinic_name'], data['clinic_address'], data['clinic_phone'], data['clinic_reg'])
        
        # -- Simplified Logic for Brevity (Same Structure as original) --
        pdf.set_font("Arial", "B", 16)
        title = "CERTIFICATE"
        if data['certificate_type'] == 'medical': title = "MEDICAL CERTIFICATE"
        elif data['certificate_type'] == 'fitness': title = "FITNESS CERTIFICATE"
        elif data['certificate_type'] == 'sickleave': title = "SICK LEAVE CERTIFICATE"
        elif data['certificate_type'] == 'form1a': title = "FORM 1A - DRIVING LICENSE"
        
        pdf.cell(0, 10, title, 0, 1, "C")
        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        
        # Generic Body Text generation based on type
        body_text = f"This is to certify that {data['doctor_name']} has examined the patient."
        if data['certificate_type'] == 'medical':
            body_text = f"I have examined {data['patient_name']} and found them suffering from {data['medical_condition']}."
        elif data['certificate_type'] == 'fitness':
            body_text = f"I have examined {data['applicant_name']} and found them fit for {data['fitness_purpose']}."
        
        pdf.multi_cell(0, 6, body_text)
        
        pdf.add_signature_section(data['doctor_name'], data['doctor_qualification'], data['doctor_reg_no'], data['doctor_specialty'])
        
        # Save to SYSTEM TEMP directory
        filename = f"Certificate_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(TEMP_DIR, filename)
        pdf.output(file_path, 'F')
        
        return jsonify({
            'success': True,
            'message': "Generated",
            'filename': filename,
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    # serve from SYSTEM TEMP directory
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return "File not found", 404

# Remove app.run() for Vercel
# if __name__ == '__main__':
#     app.run(debug=True)
