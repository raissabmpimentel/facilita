from application.models import Teacher
from application.models import Subject
from application import db

yano = Teacher('Yano', 'Edgar Toshiro Yano', 'yano@ita.br', '90', '5891')
alonso = Teacher('Alonso', 'Carlos Alberto Alonso Sanches', 'alonso.ita@gmail.com', '112', '5985')
mirisola = Teacher('Mirisola', 'Luiz Gustavo Bizarro Mirisola', 'luiz.mirisola@gmail.com', '91', '6940')
tassinafo = Teacher('Tassinafo', 'Paulo Marcelo Tasinaffo', 'tasinaffo@ita.br', '95', '6921')
duarte = Teacher('Duarte', 'Duarte Lopes de Oliveira', 'duarte@ita.br', '92', '6813')
osamu = Teacher('Osamu', 'Osamu Saotome', 'osaotome@gmail.com', '93', '5818')
jackson =  Teacher('Jackson', 'Jackson Paul Matsuura', 'jackson@ita.br', '94', '6937')
douglas =  Teacher('Douglas', 'Douglas Soares dos Santos', 'dsoares@ita.br', '187', '6928')
gabriela = Teacher('Gabriela', 'Gabriela Werner Gabriel', 'ggabriel@ita.br', '182', '6955')
manga = Teacher('Maximo', 'Marcos Ricardo Omena de Albuquerque Máximo', 'maximo.marcos@gmail.com', '188', '6958')
brutus = Teacher('Brutus', 'Brutus Abel Fratuce Pimentel', 'brutusabel@hotmail.com', '133', '5543')
db.session.add(yano)
db.session.add(alonso)
db.session.add(mirisola)
db.session.add(tassinafo)
db.session.add(duarte)
db.session.add(osamu)
db.session.add(jackson)
db.session.add(douglas)
db.session.add(gabriela)
db.session.add(manga)
db.session.add(brutus)

ces22 = Subject('CES-22', 'Programação Orientada a Objetos', 'COMP21')
ces12 = Subject('CES-12', 'Algoritmos e Estrutura de Dados II', 'COMP21')
ctc21 = Subject('CTC-21', 'Lógica Matemática e Estruturas Discretas', 'COMP21')
eea21 = Subject('EEA-21', 'Circuitos Digitais', 'COMP21')
ees10 = Subject('EES-10', 'Sistemas de Controle I', 'COMP21')
ele52 = Subject('ELE-52', 'Circuitos Eletrônicos I', 'COMP21')
cmc10 = Subject('CMC-10', 'Projeto e Fabricação de Robôs Móveis', 'Eletiva')
hum32 = Subject('HUM-32', 'Redação Acadêmica', 'Eletiva')
db.session.add(ces12)
db.session.add(ces22)
db.session.add(ctc21)
db.session.add(eea21)
db.session.add(ees10)
db.session.add(ele52)
db.session.add(cmc10)
db.session.add(hum32)

ces12.teachers.append(alonso)
ces12.teachers.append(mirisola)
ces22.teachers.append(yano)
ctc21.teachers.append(mirisola)
ctc21.teachers.append(tassinafo)
eea21.teachers.append(duarte)
eea21.teachers.append(osamu)
ees10.teachers.append(jackson)
ees10.teachers.append(gabriela)
ele52.teachers.append(douglas)
cmc10.teachers.append(manga)
hum32.teachers.append(brutus)

db.session.commit()
