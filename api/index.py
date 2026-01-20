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
                                            <input type="checkbox" id="hearingNormal" checked class="w-4 h-4 text-blue-600 rounded">
                                            <label for="hearingNormal" class="ml-2 text-sm text-gray-700">Hearing Normal</label>
                                        </div>
                                        <div class="flex items-center">
                                            <input type="checkbox" id="fitToDrive" checked class="w-4 h-4 text-blue-600 rounded">
                                            <label for="fitToDrive" class="ml-2 text-sm text-gray-700">Fit to Drive</label>
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Physical Deformity (if any)</label>
                                        <input type="text" id="physicalDeformity" placeholder="None" 
                                               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button onclick="generateCertificate('form1a')" 
                                class="w-full mt-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg font-bold text-lg hover:opacity-90 transition-opacity duration-300">
                            <i class="fas fa-file-pdf mr-2"></i> Generate Form 1A
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div id="resultSection" class="hidden mt-8 fade-in">
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-2xl font-bold text-green-600 mb-4">
                    <i class="fas fa-check-circle mr-2"></i>Certificate Generated Successfully!
                </h2>
                <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
                    <div>
                        <p class="text-gray-600">Your certificate is ready for download.</p>
                        <p class="text-sm text-gray-500 mt-1">Includes doctor's signature section and medical stamp.</p>
                    </div>
                    <a id="downloadLink" class="px-8 py-3 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg font-bold hover:opacity-90 transition-opacity duration-300">
                        <i class="fas fa-download mr-2"></i> Download PDF
                    </a>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-gray-600 text-sm">
            <p>🏥 <strong>Medical Certificate Generator</strong> | Professional Medical Documentation System</p>
            <p class="mt-2">⚠️ All certificates require doctor's signature and official seal to be valid</p>
            <p class="mt-4 text-gray-500">© 2024 Medical Certificate Generator. All rights reserved.</p>
        </div>
    </div>

    <script>
        // Set default dates
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            
            document.getElementById('leaveFrom').value = today;
            document.getElementById('leaveTo').value = nextWeek;
            document.getElementById('sickLeaveFrom').value = today;
            document.getElementById('sickLeaveTo').value = nextWeek;
        });

        function showTab(tabNumber) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById('tab' + tabNumber).classList.add('active');
            document.querySelectorAll('.tab-button')[tabNumber - 1].classList.add('active');
            
            // Hide result section
            document.getElementById('resultSection').classList.add('hidden');
        }

        async function generateCertificate(type) {
            // Collect data
            const data = {
                clinic_name: document.getElementById('clinicName').value,
                clinic_address: document.getElementById('clinicAddress').value,
                clinic_phone: document.getElementById('clinicPhone').value,
                clinic_reg: document.getElementById('clinicReg').value,
                doctor_name: document.getElementById('doctorName').value,
                doctor_qualification: document.getElementById('doctorQualification').value,
                doctor_reg_no: document.getElementById('doctorRegNo').value,
                doctor_specialty: document.getElementById('doctorSpecialty').value,
                certificate_type: type
            };

            // Validate required fields
            const requiredFields = [
                data.clinic_name,
                data.clinic_address,
                data.clinic_phone,
                data.doctor_name,
                data.doctor_qualification
            ];

            if (requiredFields.some(field => !field)) {
                alert('Please fill all required fields marked with *');
                return;
            }

            // Add type-specific data
            if (type === 'medical') {
                data.patient_name = document.getElementById('patientName').value;
                data.patient_age = document.getElementById('patientAge').value;
                data.patient_gender = document.getElementById('patientGender').value;
                data.patient_occupation = document.getElementById('patientOccupation').value;
                data.medical_condition = document.getElementById('medicalCondition').value;
                data.leave_from = document.getElementById('leaveFrom').value;
                data.leave_to = document.getElementById('leaveTo').value;
                data.additional_notes = document.getElementById('additionalNotes').value;

                if (!data.patient_name || !data.medical_condition) {
                    alert('Please fill patient name and medical condition');
                    return;
                }
            } else if (type === 'fitness') {
                data.applicant_name = document.getElementById('applicantName').value;
                data.applicant_age = document.getElementById('applicantAge').value;
                data.applicant_gender = document.getElementById('applicantGender').value;
                data.position_applied = document.getElementById('positionApplied').value;
                data.fitness_purpose = document.getElementById('fitnessPurpose').value;
                data.medical_history = document.getElementById('medicalHistory').value;
                data.fitness_remarks = document.getElementById('fitnessRemarks').value;

                if (!data.applicant_name) {
                    alert('Please fill applicant name');
                    return;
                }
            } else if (type === 'sickleave') {
                data.employee_name = document.getElementById('employeeName').value;
                data.employee_company = document.getElementById('employeeCompany').value;
                data.employee_id = document.getElementById('employeeId').value;
                data.employee_dept = document.getElementById('employeeDept').value;
                data.illness = document.getElementById('illness').value;
                data.leave_from = document.getElementById('sickLeaveFrom').value;
                data.leave_to = document.getElementById('sickLeaveTo').value;
                data.rest_advised = document.getElementById('restAdvised').checked;

                if (!data.employee_name || !data.employee_company || !data.illness) {
                    alert('Please fill employee name, company, and illness details');
                    return;
                }
            } else if (type === 'form1a') {
                data.applicant_name = document.getElementById('rtoApplicantName').value;
                data.applicant_age = document.getElementById('rtoApplicantAge').value;
                data.applicant_gender = document.getElementById('rtoApplicantGender').value;
                data.applicant_address = document.getElementById('rtoApplicantAddress').value;
                data.license_type = document.getElementById('licenseType').value;
                data.height = document.getElementById('height').value;
                data.weight = document.getElementById('weight').value;
                data.vision_right = document.getElementById('visionRight').value;
                data.vision_left = document.getElementById('visionLeft').value;
                data.color_blind = document.getElementById('colorBlind').checked;
                data.hearing_normal = document.getElementById('hearingNormal').checked;
                data.fit_to_drive = document.getElementById('fitToDrive').checked;
                data.physical_deformity = document.getElementById('physicalDeformity').value;

                if (!data.applicant_name || !data.applicant_address) {
                    alert('Please fill applicant name and address');
                    return;
                }
            }

            // Show loading state
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Generating...';
            button.disabled = true;

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    
                    if (result.success) {
                        // Show success section
                        const resultSection = document.getElementById('resultSection');
                        resultSection.classList.remove('hidden');
                        resultSection.scrollIntoView({ behavior: 'smooth' });
                        
                        // Set download link
                        const downloadLink = document.getElementById('downloadLink');
                        downloadLink.href = result.download_url;
                        downloadLink.download = result.filename;
                        
                        // Show success message
                        document.querySelector('#resultSection h2').innerHTML = 
                            `<i class="fas fa-check-circle mr-2"></i>${result.message}`;
                    } else {
                        alert('Error: ' + result.error);
                    }
                } else {
                    alert('Server error. Please try again.');
                }
            } catch (error) {
                alert('Network error. Please check your connection.');
            } finally {
                // Reset button
                button.innerHTML = originalText;
                button.disabled = false;
            }
        }
    </script>
</body>
</html>
'''

# Create stamp image
def create_stamp_image():
    stamp_path = "static/stamp.png"
    if not os.path.exists(stamp_path):
        try:
            width, height = 300, 120
            image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle([(0, 0), (width-1, height-1)], 
                         outline=(200, 0, 0, 255), width=2)
            draw.rectangle([(10, 10), (width-11, height-11)], 
                         outline=(200, 0, 0, 255), width=1)
            
            try:
                # Try to load a font
                font_large = ImageFont.truetype("arial.ttf", 20)
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
            
            image.save(stamp_path, "PNG")
        except Exception as e:
            print(f"Could not create stamp image: {str(e)}")
    return True

create_stamp_image()

class MedicalPDF(FPDF):
    """Custom PDF class for medical certificates"""
    
    def add_clinic_header(self, clinic_name, clinic_address, clinic_phone, clinic_reg):
        self.set_font("Arial", "B", 20)
        self.cell(0, 10, clinic_name, 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, clinic_address, 0, "C")
        self.cell(0, 5, f"Phone: {clinic_phone} | Email: info@clinic.com", 0, 1, "C")
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
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_certificate():
    try:
        data = request.json
        
        # Create PDF based on certificate type
        if data['certificate_type'] == 'medical':
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], 
                data['clinic_address'], 
                data['clinic_phone'], 
                data['clinic_reg']
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
                               f"{'Registration No: ' + data['doctor_reg_no'] if data.get('doctor_reg_no') else ''}, "
                               f"have examined {data['patient_name']}, {data['patient_gender']}, "
                               f"Age: {data['patient_age']} years, {data.get('patient_occupation', 'Patient')} "
                               f"on {datetime.now().strftime('%d/%m/%Y')}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"After careful examination, I hereby certify that the patient is suffering from {data['medical_condition']}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"I consider that a period of absence from duty from {leave_from.strftime('%d/%m/%Y')} "
                               f"to {leave_to.strftime('%d/%m/%Y')} ({leave_days} day(s)) is absolutely necessary "
                               f"for the restoration of his/her health.")
            
            if data.get('additional_notes'):
                pdf.ln(5)
                pdf.multi_cell(0, 6, f"Additional Recommendations: {data['additional_notes']}")
            
            pdf.add_signature_section(
                data['doctor_name'], 
                data['doctor_qualification'],
                data.get('doctor_reg_no'), 
                data.get('doctor_specialty')
            )
            
            filename = f"Medical_Certificate_{data['patient_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            message = "Medical Certificate Generated Successfully!"
            
        elif data['certificate_type'] == 'fitness':
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], 
                data['clinic_address'], 
                data['clinic_phone'], 
                data['clinic_reg']
            )
            
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "FITNESS CERTIFICATE", 0, 1, "C")
            pdf.ln(5)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.cell(0, 8, f"Certificate No: FC/{datetime.now().strftime('%Y%m%d%H%M%S')}", 0, 1)
            pdf.ln(3)
            
            pdf.multi_cell(0, 6, f"This is to certify that I, {data['doctor_name']}, {data['doctor_qualification']}"
                               f"{', Registration No: ' + data['doctor_reg_no'] if data.get('doctor_reg_no') else ''}, "
                               f"have carefully examined {data['applicant_name']}, {data['applicant_gender']}, "
                               f"Age: {data['applicant_age']} years, "
                               f"{data.get('position_applied', 'Applicant')} "
                               f"on {datetime.now().strftime('%d/%m/%Y')}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, f"Purpose: {data['fitness_purpose']}")
            
            if data.get('medical_history'):
                pdf.ln(3)
                pdf.multi_cell(0, 6, f"Previous Medical History: {data['medical_history']}")
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 6, "CERTIFICATION:")
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 6, data['fitness_remarks'])
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 6, "The applicant is MEDICALLY FIT for the above-mentioned purpose.")
            
            pdf.add_signature_section(
                data['doctor_name'], 
                data['doctor_qualification'],
                data.get('doctor_reg_no'), 
                data.get('doctor_specialty')
            )
            
            filename = f"Fitness_Certificate_{data['applicant_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            message = "Fitness Certificate Generated Successfully!"
            
        elif data['certificate_type'] == 'sickleave':
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], 
                data['clinic_address'], 
                data['clinic_phone'], 
                data['clinic_reg']
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
            
            employee_info = f"{data['employee_name']}"
            if data.get('employee_id'):
                employee_info += f", Employee ID: {data['employee_id']}"
            if data.get('employee_dept'):
                employee_info += f", {data['employee_dept']}"
            
            pdf.multi_cell(0, 6, f"This is to certify that {employee_info} has been under my medical care.")
            
            pdf.ln(3)
            pdf.multi_cell(0, 6, f"After thorough examination on {datetime.now().strftime('%d/%m/%Y')}, "
                               f"I have diagnosed the patient with {data['illness']}.")
            
            pdf.ln(3)
            pdf.multi_cell(0, 6, f"Due to this medical condition, I recommend sick leave from "
                               f"{leave_from.strftime('%d/%m/%Y')} to {leave_to.strftime('%d/%m/%Y')} "
                               f"({leave_days} day(s)).")
            
            if data.get('rest_advised'):
                pdf.ln(3)
                pdf.multi_cell(0, 6, "Complete bed rest and avoiding strenuous activities is advised during this period.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, "I request you to kindly grant the necessary leave for the recovery and restoration of health.")
            
            pdf.ln(10)
            pdf.cell(0, 6, "Thanking you,", 0, 1)
            pdf.ln(10)
            
            pdf.add_signature_section(
                data['doctor_name'], 
                data['doctor_qualification'],
                data.get('doctor_reg_no'), 
                data.get('doctor_specialty')
            )
            
            filename = f"Sick_Leave_Certificate_{data['employee_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            message = "Sick Leave Certificate Generated Successfully!"
            
        elif data['certificate_type'] == 'form1a':
            pdf = MedicalPDF()
            pdf.add_page()
            pdf.add_clinic_header(
                data['clinic_name'], 
                data['clinic_address'], 
                data['clinic_phone'], 
                data['clinic_reg']
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
            pdf.cell(0, 6, f"Gender: {data.get('applicant_gender', 'N/A')}", 0, 1)
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
            pdf.cell(0, 6, f"   Color Blindness: {'Yes' if data.get('color_blind') else 'No'}", 0, 1)
            pdf.ln(2)
            
            pdf.cell(0, 6, f"Hearing: {'Normal' if data.get('hearing_normal') else 'Impaired'}", 0, 1)
            pdf.cell(0, 6, f"Physical Deformity: {data.get('physical_deformity', 'None')}", 0, 1)
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "CERTIFICATION:", 0, 1)
            pdf.set_font("Arial", "", 11)
            
            fit_status = "MEDICALLY FIT" if data.get('fit_to_drive') else "NOT FIT"
            pdf.multi_cell(0, 6, f"I, {data['doctor_name']}, {data['doctor_qualification']}"
                               f"{', Registration No: ' + data['doctor_reg_no'] if data.get('doctor_reg_no') else ''}, "
                               f"hereby certify that I have personally examined the above-named applicant and "
                               f"find him/her {fit_status} to drive a {data['license_type']}.")
            
            pdf.ln(5)
            pdf.multi_cell(0, 6, "The applicant has been examined for any physical or mental disability that may "
                               "interfere with safe driving.")
            
            pdf.add_signature_section(
                data['doctor_name'], 
                data['doctor_qualification'],
                data.get('doctor_reg_no'), 
                data.get('doctor_specialty')
            )
            
            filename = f"Form_1A_{data['applicant_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            message = "Form 1A Generated Successfully!"
        
        # Generate PDF in memory
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        
        # Save to temporary file
        temp_dir = "tmp"
        Path(temp_dir).mkdir(exist_ok=True)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
        temp_file.write(pdf_bytes)
        temp_file.close()
        
        return jsonify({
            'success': True,
            'message': message,
            'filename': filename,
            'download_url': f'/api/download/{os.path.basename(temp_file.name)}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = os.path.join("tmp", filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename.replace('.tmp', '.pdf')
        )
    return "File not found", 404

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)
