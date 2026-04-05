from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_sop(filename, title, sample_type):
    doc = Document()
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    
    # ТИТУЛЬНЫЙ ЛИСТ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("СИСТЕМА МЕНЕДЖМЕНТА КАЧЕСТВА ГАУЗ «ООКЦХТ»\n\n")
    run.bold = True
    run.font.size = Pt(16)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Стандартная операционная процедура\n\n")
    run.bold = True
    run.font.size = Pt(14)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Направление стандартизации: Лабораторная диагностика\n\n")
    run.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{title}\n\n")
    run.bold = True
    run.font.size = Pt(16)
    
    for _ in range(8):
        doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("г. Оренбург, 2026")
    run.font.size = Pt(14)
    
    # Лист согласования
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ЛИСТ СОГЛАСОВАНИЯ:\n")
    run.bold = True
    
    doc.add_paragraph("\nРазработал:")
    doc.add_paragraph("Заведующий КДЛ _________________ / _________________/")
    doc.add_paragraph("\nПроверил:")
    doc.add_paragraph("Ответственный за качество _________________ / _________________/")
    doc.add_paragraph("\nУтвердил:")
    doc.add_paragraph("Главный врач ГАУЗ «ООКЦХТ» _________________ / _________________/")
    
    # ОГЛАВЛЕНИЕ
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ОГЛАВЛЕНИЕ\n")
    run.bold = True
    
    sections = [
        "1. Область применения",
        "2. Нормативные ссылки",
        "3. Термины и определения",
        "4. Обозначения и сокращения",
        "5. Основные нормативные положения",
        "5.1. Требования безопасности",
        "5.2. Требования к персоналу",
        "5.3. Требования к помещению и оборудованию",
        "5.4. Процедура выполнения работ",
        "5.5. Оформление и регистрация результатов",
        "5.6. Контроль качества",
        "6. Приложения",
        "7. Лист регистрации изменений"
    ]
    for section in sections:
        doc.add_paragraph(section)
    
    # 1. ОБЛАСТЬ ПРИМЕНЕНИЯ
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("1. ОБЛАСТЬ ПРИМЕНЕНИЯ\n")
    run.bold = True
    
    doc.add_paragraph(f"Настоящая стандартная операционная процедура (СОП) распространяется на процедуру преаналитического этапа исследования {sample_type} в клинико-диагностической лаборатории ГАУЗ «ООКЦХТ».")
    doc.add_paragraph(f"СОП обязательна для исполнения всеми сотрудниками КДЛ, участвующими в процессе приема, регистрации, центрифугирования и подготовки {sample_type} к исследованию.")
    doc.add_paragraph("Область применения включает:")
    doc.add_paragraph("- прием и регистрацию биологического материала;", indent_level=1)
    doc.add_paragraph("- оценку пригодности проб для исследования;", indent_level=1)
    doc.add_paragraph("- центрифугирование и подготовку проб;", indent_level=1)
    doc.add_paragraph("- хранение и транспортировку внутри лаборатории.", indent_level=1)
    
    # 2. НОРМАТИВНЫЕ ССЫЛКИ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n2. НОРМАТИВНЫЕ ССЫЛКИ\n")
    run.bold = True
    
    doc.add_paragraph("При разработке СОП использованы следующие нормативные документы:")
    doc.add_paragraph("- ГОСТ ISO 15189-2015 «Лаборатории медицинские. Требования к качеству и компетентности»;", indent_level=1)
    doc.add_paragraph("- ГОСТ Р 53434-2009 «Принципы надлежащей лабораторной практики»;", indent_level=1)
    doc.add_paragraph("- МУ 4.2.2039-05 «Техника сбора и транспортировки биоматериалов в микробиологические лаборатории»;", indent_level=1)
    doc.add_paragraph("- СанПиН 1.2.3685-21 «Гигиенические нормативы и требования к обеспечению безопасности и (или) безвредности для человека факторов среды обитания»;", indent_level=1)
    doc.add_paragraph("- СП 1.3.3686-21 «Санитарно-эпидемиологические требования по профилактике инфекционных болезней»;", indent_level=1)
    doc.add_paragraph("- Приказ Минздрава РФ № 203н от 13.04.2022 «Об утверждении требований к проведению лабораторных исследований».", indent_level=1)
    
    # 3. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n3. ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ\n")
    run.bold = True
    
    para = doc.add_paragraph()
    run = para.add_run("Биологический материал: ")
    run.bold = True
    para.add_run(f"{sample_type}, полученная от пациента для лабораторного исследования")
    
    para = doc.add_paragraph()
    run = para.add_run("Преаналитический этап: ")
    run.bold = True
    para.add_run("Этап лабораторного исследования, включающий назначение исследования, подготовку пациента, взятие биоматериала, его доставку, регистрацию, сортировку, центрифугирование и хранение")
    
    para = doc.add_paragraph()
    run = para.add_run("Гемолиз: ")
    run.bold = True
    para.add_run("Разрушение эритроцитов с выходом гемоглобина в окружающую среду")
    
    para = doc.add_paragraph()
    run = para.add_run("Контаминация: ")
    run.bold = True
    para.add_run("Загрязнение пробы посторонними веществами или микроорганизмами")
    
    para = doc.add_paragraph()
    run = para.add_run("Пригодность пробы: ")
    run.bold = True
    para.add_run("Соответствие принятой пробы установленным критериям качества")
    
    if "ликвор" in sample_type.lower():
        para = doc.add_paragraph()
        run = para.add_run("Ликвор: ")
        run.bold = True
        para.add_run("Спинномозговая жидкость, циркулирующая в желудочках головного мозга и субарахноидальном пространстве")
    else:
        para = doc.add_paragraph()
        run = para.add_run("Плевральная жидкость: ")
        run.bold = True
        para.add_run("Серозная жидкость, накапливающаяся в плевральной полости при патологических состояниях")
    
    # 4. ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n4. ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ\n")
    run.bold = True
    
    abbreviations = [
        "СОП – стандартная операционная процедура",
        "КДЛ – клинико-диагностическая лаборатория",
        "ГАУЗ «ООКЦХТ» – Государственное автономное учреждение здравоохранения «Оренбургский областной клинический центр хирургии и травматологии»",
        "ИС – информационная система",
        "ПК – персональный компьютер",
        "СИЗ – средства индивидуальной защиты",
        "ЦФ – центрифуга",
    ]
    if "ликвор" in sample_type.lower():
        abbreviations.append("СМЖ – спинномозговая жидкость (ликвор)")
    else:
        abbreviations.append("ПЖ – плевральная жидкость")
    
    for abbr in abbreviations:
        doc.add_paragraph(abbr)
    
    # 5. ОСНОВНЫЕ НОРМАТИВНЫЕ ПОЛОЖЕНИЯ
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n5. ОСНОВНЫЕ НОРМАТИВНЫЕ ПОЛОЖЕНИЯ\n")
    run.bold = True
    
    p = doc.add_paragraph()
    run = p.add_run("5.1. Требования безопасности\n")
    run.bold = True
    
    doc.add_paragraph("Все работы с биологическим материалом проводятся с соблюдением мер биологической безопасности:")
    doc.add_paragraph("- персонал должен работать в спецодежде (халат, шапочка, сменная обувь);", indent_level=1)
    doc.add_paragraph("- обязательно использование СИЗ: перчатки, маска, защитные очки;", indent_level=1)
    doc.add_paragraph("- все манипуляции проводятся в боксе для работы с биологическим материалом;", indent_level=1)
    doc.add_paragraph("- запрещается прием пищи, курение, нанесение косметики в рабочей зоне;", indent_level=1)
    doc.add_paragraph("- поверхности рабочих столов дезинфицируются до и после работы;", indent_level=1)
    doc.add_paragraph("- при попадании биоматериала на кожу или слизистые немедленно провести обработку согласно инструкции;", indent_level=1)
    doc.add_paragraph("- отходы классов Б и В собираются в маркированную тару согласно СанПиН.", indent_level=1)
    
    p = doc.add_paragraph()
    run = p.add_run("5.2. Требования к персоналу\n")
    run.bold = True
    
    doc.add_paragraph("К работе допускаются сотрудники:")
    doc.add_paragraph("- прошедшие обучение по специальности «Лабораторная диагностика»;", indent_level=1)
    doc.add_paragraph("- ознакомленные с настоящей СОП под роспись;", indent_level=1)
    doc.add_paragraph("- прошедшие инструктаж по технике безопасности;", indent_level=1)
    doc.add_paragraph("- имеющие действующий сертификат/аккредитацию;", indent_level=1)
    doc.add_paragraph("- прошедшие медицинский осмотр и вакцинацию согласно требованиям.", indent_level=1)
    
    p = doc.add_paragraph()
    run = p.add_run("5.3. Требования к помещению и оборудованию\n")
    run.bold = True
    
    doc.add_paragraph("Работы проводятся в помещении КДЛ, соответствующем требованиям:")
    doc.add_paragraph("- температура воздуха 18-22°С;", indent_level=1)
    doc.add_paragraph("- влажность 40-60%;", indent_level=1)
    doc.add_paragraph("- наличие приточно-вытяжной вентиляции;", indent_level=1)
    doc.add_paragraph("- оснащение рабочими столами с моющейся поверхностью;", indent_level=1)
    doc.add_paragraph("- наличие холодильного оборудования (2-8°С);", indent_level=1)
    doc.add_paragraph("- центрифуга с герметичными роторами;", indent_level=1)
    doc.add_paragraph("- микроскопы, анализаторы согласно профилю исследований;", indent_level=1)
    doc.add_paragraph("- компьютеры с доступом к ИС.", indent_level=1)
    
    p = doc.add_paragraph()
    run = p.add_run("5.4. Процедура выполнения работ\n")
    run.bold = True
    
    doc.add_paragraph("5.4.1. Прием и регистрация биологического материала")
    doc.add_paragraph("При поступлении пробирок с биоматериалом сотрудник КДЛ обязан:", indent_level=1)
    doc.add_paragraph("- проверить целостность пробирки (отсутствие трещин, протечек);", indent_level=2)
    doc.add_paragraph("- сверить данные на направлении и этикетке (ФИО пациента, дата рождения, номер истории болезни, дата и время взятия материала);", indent_level=2)
    doc.add_paragraph("- оценить объем достаточности материала (не менее 1-2 мл для большинства исследований);", indent_level=2)
    doc.add_paragraph("- визуально оценить внешний вид материала (цвет, прозрачность, наличие хлопьев, крови);", indent_level=2)
    doc.add_paragraph("- зарегистрировать пробу в ИС с присвоением уникального номера;", indent_level=2)
    doc.add_paragraph("- указать дату и время приема материала.", indent_level=2)
    
    doc.add_paragraph("5.4.2. Критерии приемлемости проб")
    doc.add_paragraph(f"Пробы {sample_type} признаются пригодными при соблюдении условий:", indent_level=1)
    doc.add_paragraph("- правильное оформление сопроводительной документации;", indent_level=2)
    doc.add_paragraph("- соблюдение температурного режима транспортировки;", indent_level=2)
    if "плевральн" in sample_type.lower():
        doc.add_paragraph("- отсутствие признаков гемолиза;", indent_level=2)
    doc.add_paragraph("- достаточный объем материала;", indent_level=2)
    if "ликвор" in sample_type.lower():
        doc.add_paragraph("- соблюдение сроков доставки (ликвор доставляется немедленно).", indent_level=2)
    else:
        doc.add_paragraph("- соблюдение сроков доставки (в течение 1 часа).", indent_level=2)
    
    doc.add_paragraph("Непригодные пробы не принимаются. Составляется акт с указанием причины отказа. Лечащий врач уведомляется немедленно.")
    
    doc.add_paragraph("5.4.3. Центрифугирование и подготовка проб")
    doc.add_paragraph("Подготовка проб проводится следующим образом:", indent_level=1)
    if "ликвор" in sample_type.lower():
        doc.add_paragraph("- ликвор аккуратно перемешивают путем переворачивания пробирки;", indent_level=2)
        doc.add_paragraph("- для цитологического исследования готовят нативные препараты сразу после получения;", indent_level=2)
        doc.add_paragraph("- для биохимических исследований центрифугируют при 1500-2000 об/мин в течение 10 минут;", indent_level=2)
        doc.add_paragraph("- надосадочную жидкость переносят в чистую пробирку;", indent_level=2)
        doc.add_paragraph("- осадок используют для микроскопического исследования.", indent_level=2)
    else:
        doc.add_paragraph("- плевральную жидкость аккуратно перемешивают;", indent_level=2)
        doc.add_paragraph("- для цитологического исследования часть материала фиксируют;", indent_level=2)
        doc.add_paragraph("- для биохимических и микробиологических исследований центрифугируют при 2000-3000 об/мин в течение 15 минут;", indent_level=2)
        doc.add_paragraph("- надосадочную жидкость разделяют на аликвоты;", indent_level=2)
        doc.add_paragraph("- осадок используют для микроскопии и посева.", indent_level=2)
    
    doc.add_paragraph("5.4.4. Хранение и транспортировка")
    doc.add_paragraph("Условия хранения подготовленных проб:", indent_level=1)
    doc.add_paragraph("- при температуре 2-8°С не более 24 часов;", indent_level=2)
    doc.add_paragraph("- замораживание допускается только для биохимических исследований (-20°С);", indent_level=2)
    doc.add_paragraph("- повторное замораживание-оттаивание запрещено;", indent_level=2)
    doc.add_paragraph("- транспортировка внутри лаборатории осуществляется в закрытых контейнерах.", indent_level=2)
    
    p = doc.add_paragraph()
    run = p.add_run("5.5. Оформление и регистрация результатов\n")
    run.bold = True
    
    doc.add_paragraph("Результаты исследований оформляются в ИС и включают:")
    doc.add_paragraph("- дату и время выполнения исследования;", indent_level=1)
    doc.add_paragraph("- наименование исследуемого материала;", indent_level=1)
    doc.add_paragraph("- полученные значения с указанием единиц измерения;", indent_level=1)
    doc.add_paragraph("- референсные интервалы;", indent_level=1)
    doc.add_paragraph("- отметку о флагах отклонений;", indent_level=1)
    doc.add_paragraph("- ФИО исполнителя.", indent_level=1)
    
    doc.add_paragraph("Результаты передаются лечащему врачу через ИС или на бумажном носителе.")
    
    p = doc.add_paragraph()
    run = p.add_run("5.6. Контроль качества\n")
    run.bold = True
    
    doc.add_paragraph("Контроль качества на преаналитическом этапе включает:")
    doc.add_paragraph("- ежедневный мониторинг температуры холодильников;", indent_level=1)
    doc.add_paragraph("- проверку исправности центрифуг;", indent_level=1)
    doc.add_paragraph("- регистрацию всех случаев отбраковки проб;", indent_level=1)
    doc.add_paragraph("- проведение внутрилабораторного контроля качества;", indent_level=1)
    doc.add_paragraph("- участие в программах внешней оценки качества (ФСВОК).", indent_level=1)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("\n6. ПРИЛОЖЕНИЯ\n")
    run.bold = True
    
    doc.add_paragraph("Приложение А. Форма журнала регистрации проб")
    doc.add_paragraph("Приложение Б. Критерии отбраковки биологического материала")
    doc.add_paragraph("Приложение В. Схема действий при аварийных ситуациях")
    
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("7. ЛИСТ РЕГИСТРАЦИИ ИЗМЕНЕНИЙ\n")
    run.bold = True
    
    table = doc.add_table(rows=6, cols=5)
    table.style = 'Table Grid'
    
    headers = ["№ версии", "Дата введения", "Основание изменения", "Содержание изменения", "Ответственный"]
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True
    
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ЛИСТ ОЗНАКОМЛЕНИЯ СО СТАНДАРТОМ\n")
    run.bold = True
    
    doc.add_paragraph("\nСтруктурное подразделение: Клинико-диагностическая лаборатория")
    
    table2 = doc.add_table(rows=6, cols=4)
    table2.style = 'Table Grid'
    
    headers2 = ["№ п/п", "ФИО сотрудника", "Должность", "Дата ознакомления"]
    for i, header in enumerate(headers2):
        cell = table2.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True
    
    doc.save(filename)
    print(f"Created: {filename}")

if __name__ == "__main__":
    create_sop("СОП_Ликвор.docx", "ПРИЕМ, РЕГИСТРАЦИЯ И ПОДГОТОВКА ЛИКВОРА К ИССЛЕДОВАНИЮ", "спинномозговой жидкости (ликвора)")
    create_sop("СОП_Плевральная_жидкость.docx", "ПРИЕМ, РЕГИСТРАЦИЯ И ПОДГОТОВКА ПЛЕВРАЛЬНОЙ ЖИДКОСТИ К ИССЛЕДОВАНИЮ", "плевральной жидкости")
    print("Done!")
