from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'bungabudi29#'  # Buat enkripsi data

with open('questions.json') as f: # Baca pertanyaan dari json
    data = json.load(f)

@app.route('/')
def home():
    num_levels = len(data['levels'])  # Ngitung jumlah level di json
    if 'completed_level' not in session or len(session['completed_level']) != num_levels:
        # Biar jumlah levelnya sinkron
        session['completed_level'] = [True] + [False] * (num_levels - 1)
    session['level_now'] = 1
    session['score'] = 0
    session['user_answers'] = []
    return render_template('home.html')

@app.route('/levels')
def levels():
    return render_template('levels.html', completed_level=session.get('completed_level', [True, False, False, False])) #baru level 1 yang kebuka

@app.route('/level/<int:level>')
def start_level(level):
    session['level_now'] = level
    session['question_index'] = 0
    session['score'] = 0
    session['user_answers'] = []  # reset jawaban kalo ke level berikutnya
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    level = session['level_now']
    index = session['question_index']

    # bakal redirect ke hasil kalo semua pertanyaan udah selesai
    if index >= len(data['levels'][str(level)]):
        return redirect(url_for('result'))

    question = data['levels'][str(level)][index]

    feedback = None  # buat nyimpen apakah jawabannya benar atau salah
    if request.method == 'POST':
        answer = request.form['answer'].strip().lower()  # Normalisasi jawaban pengguna
        correct_answer = question['answer'].strip().lower()  # Normalisasi jawaban benar
        
        correct = answer == correct_answer

        # Debugging: print jawaban buat verifikasi
        print(f"Jawaban user: {answer}, Kunci jawaban: {correct_answer}, Cocok: {correct}")

        # feedback ke user: ngasih tau jawaban user tuh bener atau salah
        if correct:
            session['score'] += 1
            feedback = "Wih benerr mantap!"
        else:
            feedback = f"Salah awokawokawok, harusnya: {question['answer']}"

        session['question_index'] += 1
        session['feedback'] = feedback  # simpan feedback ke session
        return redirect(url_for('question'))

    feedback = session.pop('feedback', None)  # Ambil feedback dari session kalo ada
    return render_template('question.html', question=question, feedback=feedback)

@app.route('/result')
def result():
    level = session['level_now']
    total_questions = len(data['levels'][str(level)])
    score = (session['score'] / total_questions) * 100

    # Debug: cetak informasi tentang level
    print(f"Level {level} selesai dengan skor {score}%")
    print(f"Status sebelum update: {session['completed_level']}")

    # Update status level jika skor lebih dari 60%
    if score > 60:
        session['completed_level'][level - 1] = True  # Tandai level saat ini selesai
        if level < len(session['completed_level']):  # Buka level berikutnya
            session['completed_level'][level] = True
        session.modified = True  # Wajib untuk menyimpan perubahan session

    # Debug: cetak informasi setelah update
    print(f"Status setelah update: {session['completed_level']}")

    return render_template(
        'result.html',
        result=score,
        level=level,
        completed_level=session['completed_level']
    )

if __name__ == '__main__':
    app.run(debug=True)