import sqlite3
import pandas as pd


def get_mark_id(mark: str):
    mark = int(mark)
    if mark < 10:
        return '1'
    if mark < 20:
        return '2'
    if mark < 30:
        return '3'
    if mark < 40:
        return '4'
    if mark < 50:
        return '5'
    if mark < 60:
        return '6'
    if mark < 70:
        return '7'
    if mark < 80:
        return '8'
    if mark < 90:
        return '9'
    if mark < 100:
        return '10'



db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS university (
id INTEGER PRIMARY KEY,
name_univer TEXT,
name_napr TEXT,
platno TEXT,
subjects TEXT,
subjects_mark TEXT,
minimum_last INTEGER,
link TEXT
)
''')
db.commit()
i = 0
query = 'INSERT INTO university (id,name_univer,name_napr,platno,subjects,subjects_mark,minimum_last,link) values (?,?,?,?,?,?,?,?)'
with open(r'subjects.txt', encoding='UTF-8') as f:
    subjects_arr = list(map(str.strip, f.readlines()))
n = int(input())
while i < n:
    napravlenie = input('Направление: ')
    predmet1 = input('Предмет: ').strip()
    predmet1_id = str(subjects_arr.index(predmet1))
    mark1 = input('Балл: ').strip()
    mark1 = get_mark_id(mark1)

    predmet2 = input('Предмет: ').strip()
    predmet2_id = str(subjects_arr.index(predmet2))
    mark2 = input('Балл: ').strip()
    mark2 = get_mark_id(mark2)

    predmet3 = input('Предмет: ').strip()
    predmet3_id = str(subjects_arr.index(predmet3))
    mark3 = input('Балл: ').strip()
    mark3 = get_mark_id(mark3)
    minn = input('Minimum last year: ')
    subj = ' '.join([predmet1_id, predmet2_id, predmet3_id])
    marks = ' '.join([mark1, mark2, mark3])
    link = input('Link: ')
    cursor.execute(
        query,
        (
            i,
            'ВШЭ',
            napravlenie,
            'False',
            subj,
            marks,
            int(minn),
            link
        )
    )
    db.commit()
    i += 1
query = 'SELECT * from university'
df = pd.read_sql_query(query, db)
print(df.head())
