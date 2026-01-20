import os
import tempfile
from datetime import datetime, date
from pathlib import Path
from flask import Flask, request, send_file, jsonify, render_template_string
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Create necessary directories
Path("static").mkdir(exist_ok=True)
Path("tmp").mkdir(exist_ok=True)

# HTML Template
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
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .tab-button.active {
            background-color: #667eea;
            color: white;
        }
        .certificate-preview {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 20px;
            background: white;
            min-height: 500px;
        }
        .required::after {
            content: " *";
            color: red;
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="p-4 md:p-6">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6 text-center">
            <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">
                <i class="fas fa-hospital text-blue-500 mr-3"></i>Medical Certificate Generator
            </h1>
            <p class="text-gray-600">Professional Medical & Fitness Certificates</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Sidebar -->
            <div class="lg:col-span-1">
                <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">
                        <i class="fas fa-hospital text-blue-500 mr-2"></i>Clinic Information
                    </h2>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Clinic Name</label>
                            <input type="text" id="clinicName" value="City Medical Center" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Clinic Address</label>
                            <textarea id="clinicAddress" rows="3" 
                                      class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">123 Medical Street, City, State - 560001</textarea>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Contact Number</label>
                            <input type="text" id="clinicPhone" value="+91 9876543210" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Registration Number</label>
                            <input type="text" id="clinicReg" value="REG/2024/MC001" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                    </div>
                    
                    <h2 class="text-xl font-bold text-gray-800 mt-6 mb-4">
                        <i class="fas fa-user-md text-green-500 mr-2"></i>Doctor Details
                    </h2>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Doctor Name</label>
                            <input type="text" id="doctorName" value="Dr. Ramesh Kumar" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Qualification</label>
                            <input type="text" id="doctorQualification" value="MBBS, MD (General Medicine)" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Medical Registration No.</label>
                            <input type="text" id="doctorRegNo" value="MCI-12345" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
                            <input type="text" id="doctorSpecialty" value="General Physician" 
                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>
                    </div>
                </div>
                
                <div class="bg-blue-50 rounded-xl p-6">
                    <h3 class="font-bold text-blue-800 mb-2">
                        <i class="fas fa-info-circle mr-2"></i>Important Notes
                    </h3>
                    <ul class="text-sm text-blue-700 space-y-1">
                        <li><i class="fas fa-check-circle mr-2"></i>All fields marked * are required</li>
                        <li><i class="fas fa-check-circle mr-2"></i>Certificates include automatic stamp</li>
                        <li><i class="fas fa-check-circle mr-2"></i>For official use only</li>
                        <li><i class="fas fa-check-circle mr-2"></i>Doctor's signature required for validity</li>
                    </ul>
                </div>
            </div>

            <!-- Main Content -->
            <div class="lg:col-span-2">
                <!-- Tabs -->
                <div class="bg-white rounded-xl shadow-lg p-4 mb-6">
                    <div class="flex flex-wrap gap-2">
                        <button onclick="showTab(1)" class="tab-button active px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center">
                            <i class="fas fa-file-medical mr-2"></i> Medical Certificate
                        </button>
                        <button onclick="showTab(2)" class="tab-button px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center">
                            <i class="fas fa-dumbbell mr-2"></i> Fitness Certificate
                        </button>
                        <button onclick="showTab(3)" class="tab-button px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center">
                            <i class="fas fa-procedures mr-2"></i> Sick Leave
                        </button>
                        <button onclick="showTab(4)" class="tab-button px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center">
                            <i class="fas fa-car mr-2"></i> Form 1A (RTO)
                        </button>
                    </div>
                </div>

                <!-- Tab Contents -->
                <div id="tab1" class="tab-content active">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">
                            <i class="fas fa-file-medical text-red-500 mr-2"></i>Medical Certificate
                        </h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Patient Info -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Patient Information</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Patient Name</label>
                                        <input type="text" id="patientName" placeholder="Enter patient name" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Age</label>
                                            <input type="number" id="patientAge" value="30" min="0" max="120"
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                                            <select id="patientGender" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                                <option>Male</option>
                                                <option>Female</option>
                                                <option>Other</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
                                        <input type="text" id="patientOccupation" placeholder="Enter occupation" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Medical Details -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Medical Details</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Medical Condition</label>
                                        <textarea id="medicalCondition" rows="3" placeholder="E.g., Viral Fever, Acute Gastroenteritis"
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Leave From</label>
                                            <input type="date" id="leaveFrom" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Leave To</label>
                                            <input type="date" id="leaveTo" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
                                        <textarea id="additionalNotes" rows="2" placeholder="E.g., Complete bed rest advised"
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button onclick="generateCertificate('medical')" 
                                class="w-full mt-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity duration-300">
                            <i class="fas fa-file-pdf mr-2"></i> Generate Medical Certificate
                        </button>
                    </div>
                </div>

                <!-- Add similar tab contents for other certificates -->
                <!-- Tab 2: Fitness Certificate -->
                <div id="tab2" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">
                            <i class="fas fa-dumbbell text-green-500 mr-2"></i>Fitness Certificate
                        </h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Applicant Info -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Applicant Information</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Applicant Name</label>
                                        <input type="text" id="applicantName" placeholder="Enter applicant name" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Age</label>
                                            <input type="number" id="applicantAge" value="25" min="0" max="120"
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                                            <select id="applicantGender" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                                <option>Male</option>
                                                <option>Female</option>
                                                <option>Other</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Position Applied</label>
                                        <input type="text" id="positionApplied" placeholder="Enter position" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Fitness Details -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Fitness Details</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Purpose</label>
                                        <select id="fitnessPurpose" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                            <option>Government Service</option>
                                            <option>Private Job</option>
                                            <option>Promotion</option>
                                            <option>Transfer</option>
                                            <option>Sports/Athletics</option>
                                            <option>Other</option>
                                        </select>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Medical History</label>
                                        <textarea id="medicalHistory" rows="3" placeholder="Previous medical history (if any)"
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Remarks</label>
                                        <textarea id="fitnessRemarks" rows="2" 
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">The applicant is medically fit and has no physical disabilities that would prevent them from performing their duties.</textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button onclick="generateCertificate('fitness')" 
                                class="w-full mt-6 bg-gradient-to-r from-green-500 to-blue-500 text-white py-3 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity duration-300">
                            <i class="fas fa-file-pdf mr-2"></i> Generate Fitness Certificate
                        </button>
                    </div>
                </div>

                <!-- Tab 3: Sick Leave Certificate -->
                <div id="tab3" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">
                            <i class="fas fa-procedures text-orange-500 mr-2"></i>Sick Leave Certificate
                        </h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Employee Info -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Employee Information</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Employee Name</label>
                                        <input type="text" id="employeeName" placeholder="Enter employee name" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Company/Organization</label>
                                        <input type="text" id="employeeCompany" placeholder="Enter company name" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
                                            <input type="text" id="employeeId" placeholder="EMP001" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Department</label>
                                            <input type="text" id="employeeDept" placeholder="Sales" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Leave Details -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Leave Details</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Illness/Condition</label>
                                        <textarea id="illness" rows="3" placeholder="E.g., Acute Upper Respiratory Tract Infection"
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Leave From</label>
                                            <input type="date" id="sickLeaveFrom" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1 required">Leave To</label>
                                            <input type="date" id="sickLeaveTo" 
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                    </div>
                                    
                                    <div class="flex items-center space-x-4">
                                        <div class="flex items-center">
                                            <input type="checkbox" id="restAdvised" checked class="w-4 h-4 text-blue-600 rounded">
                                            <label for="restAdvised" class="ml-2 text-sm text-gray-700">Complete bed rest advised</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button onclick="generateCertificate('sickleave')" 
                                class="w-full mt-6 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity duration-300">
                            <i class="fas fa-file-pdf mr-2"></i> Generate Sick Leave Certificate
                        </button>
                    </div>
                </div>

                <!-- Tab 4: Form 1A -->
                <div id="tab4" class="tab-content">
                    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">
                            <i class="fas fa-car text-purple-500 mr-2"></i>Form 1A - Driving License
                        </h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Applicant Info -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Applicant Information</h3>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Applicant Name</label>
                                        <input type="text" id="rtoApplicantName" placeholder="Enter applicant name" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Age</label>
                                            <input type="number" id="rtoApplicantAge" value="25" min="16" max="100"
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                                            <select id="rtoApplicantGender" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                                <option>Male</option>
                                                <option>Female</option>
                                                <option>Other</option>
                                            </select>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">Address</label>
                                        <textarea id="rtoApplicantAddress" rows="3" placeholder="Enter complete address"
                                                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1 required">License Type</label>
                                        <select id="licenseType" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                            <option>Two Wheeler</option>
                                            <option>Four Wheeler (LMV)</option>
                                            <option>Transport Vehicle</option>
                                            <option>Commercial Vehicle</option>
                                            <option>Renewal</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Medical Examination -->
                            <div>
                                <h3 class="text-lg font-semibold text-gray-700 mb-4">Medical Examination</h3>
                                <div class="space-y-4">
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Height (cm)</label>
                                            <input type="number" id="height" value="170" min="100" max="250"
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Weight (kg)</label>
                                            <input type="number" id="weight" value="70" min="30" max="200"
                                                   class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        </div>
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Vision - Right Eye</label>
                                            <select id="visionRight" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                                <option>6/6</option>
                                                <option>6/9</option>
                                                <option>6/12</option>
                                                <option>6/18</option>
                                                <option>6/24</option>
                                                <option>6/36</option>
                                                <option>6/60</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-gray-700 mb-1">Vision - Left Eye</label>
                                            <select id="visionLeft" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
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
                                    
                                    <div class="space-y-2">
                                        <div class="flex items-center">
                                            <input type="checkbox" id="colorBlind" class="w-4 h-4 text-blue-600 rounded">
                                            <label for="colorBlind" class="ml-2 text-sm text-gray-700">Color Blindness Detected</label>
                                        </div>
                                        <div class="flex items-center">
                                            <input type="checkbox" id="hearingNormal" checked class="w-4
