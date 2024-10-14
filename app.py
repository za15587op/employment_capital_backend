from flask import Flask, request, jsonify
from sklearn.neighbors import NearestNeighbors
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://employment-capital.vercel.app", "http://localhost:3000"]
    }
})  # Enable CORS for Vercel and localhost

def create_feature_vector(data):
    try:
        print(data,"data123")
        # ตรวจสอบว่าแต่ละฟิลด์ที่จำเป็นมีอยู่หรือไม่
        missing_fields = []
        if 'skill_type_name' not in data:
            missing_fields.append('ชื่อทักษะ (skill_type_name)')
        if 'skill_level' not in data:
            missing_fields.append('ระดับทักษะ (skill_level)')
        if 'availability_time' not in data:
            missing_fields.append('ช่วงเวลาที่พร้อมทำงาน (availability_time)')
        if 'availability_days' not in data:
            missing_fields.append('วันที่พร้อมทำงาน (availability_days)')

        # หากฟิลด์ใดหายไป จะยกข้อผิดพลาดพร้อมกับระบุฟิลด์ที่หายไป
        if missing_fields:
            raise KeyError(f"ข้อมูลไม่ครบ: ต้องมี {', '.join(missing_fields)}")

        # ข้อมูลสำหรับตรวจสอบขนาดและเนื้อหาของข้อมูลที่รับมา
        print('ประเภททักษะ:', data['skill_type_name'])
        print('ระดับทักษะ:', data['skill_level'])
        print('ช่วงเวลาที่พร้อมทำงาน:', data['availability_time'])
        print('วันที่พร้อมทำงาน:', data['availability_days'])

        # รวมข้อมูลทั้งหมดเป็นเวกเตอร์เดียว
        feature_vector = np.array([*data["skill_type_name"], *data["skill_level"], *data["availability_time"], *data["availability_days"]])

        # ข้อมูลสำหรับตรวจสอบเวกเตอร์ที่สร้างขึ้น
        print('เวกเตอร์ที่สร้างขึ้น:', feature_vector)
        
        return feature_vector

    except KeyError as e:
        print(f"เกิดข้อผิดพลาดใน create_feature_vector: {e}")
        raise


@app.route('/match', methods=['POST'])
def match_students():
    try:
        data = request.json
        
        print(data,"data match")

        if not data or 'organizations' not in data or 'students' not in data:
            return jsonify({"error": "Invalid input data. 'organizations' and 'students' are required."}), 400

        organizations = data['organizations']
        students = data['students']

        # Log the incoming data for debugging
        print('Received organization data:', organizations)
        print('Received student data:', students)

        # Create feature vectors for students
        student_vectors = np.array([create_feature_vector(student) for student in students])
        org_vector = create_feature_vector(organizations[0]).reshape(1, -1)

        # Use k-NN for matching
        model = NearestNeighbors(n_neighbors=len(students), metric='euclidean')
        model.fit(student_vectors)
        distances, indices = model.kneighbors(org_vector)

        # Prepare the matches
        matches = [{"Organization ID": organizations[0]["organization_id"], "Student ID": students[i]["student_id"], "Distance": float(distances[0][j])}  # แปลง np.float64 เป็น float
                   for j, i in enumerate(indices[0])]
        print(matches)
        
        #ทำให้เรียงจากน้อยไปมาก
        matches_sorted = sorted(matches, key=lambda x: x["Distance"])
        
        print(matches_sorted)
        
        return jsonify(matches_sorted), 200

    except Exception as e:
        # Return the error message in the response along with a status code
        print(f"Error in match_students: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
