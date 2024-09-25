# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 2024
@author: Sebastian Suarez
"""

# Imports
import sys
import traceback
from colorama import Fore
from decouple import config
from app.CreacionMasivaPacientes.controllers.getInfoExcel_controller import (
    obtener_datos_excel,
)
from app.Services.readListJSON import leer_json, normalize_string


KEY_GOMEDISYS_PROD = config("KEY_GOMEDISYS_PROD")
LIST_ptTypeDocument = config("LIST_ptTypeDocument")
LIST_ptAdministrativeSex = config("LIST_ptAdministrativeSex")
LIST_ptGenderIdentity = config("LIST_ptGenderIdentity")
LIST_ptMaritalStatus = config("LIST_ptMaritalStatus")
LIST_ptScholarship = config("LIST_ptScholarship")
LIST_ptOccupation = config("LIST_ptOccupation")
LIST_PtReligion = config("LIST_PtReligion")
LIST_ptZoneResidence = config("LIST_ptZoneResidence")
LIST_ptCareProvider = config("LIST_ptCareProvider")
LIST_ptPoliticalDivision = config("LIST_ptPoliticalDivision")
LIST_PtReligion = config("LIST_PtReligion")
LIST_OFFICES = config("OFFICES")


# Obtener datos necesarios antes del bucle
type_documents = leer_json(LIST_ptTypeDocument)
administrative_sexes = leer_json(LIST_ptAdministrativeSex)
marital_statuses = leer_json(LIST_ptMaritalStatus)
scholarships = leer_json(LIST_ptScholarship)
occupations = leer_json(LIST_ptOccupation)
religions = leer_json(LIST_PtReligion)
care_providers = leer_json(LIST_ptCareProvider)
zones_residence = leer_json(LIST_ptZoneResidence)
political_division = leer_json(LIST_ptPoliticalDivision)
offices = leer_json(LIST_OFFICES)

# Controller
async def create_body_request(paciente_data):
    try:
        # Convertir a un diccionario para búsquedas más eficientes
        ptPoliticalDivision_dict = {
            normalize_string(division["Name"]): division["Id"]
            for division in political_division
        }
        ptPoliticalDivision_HomeAddress = {
            normalize_string(division["Name"]): division["Id"]
            for division in political_division
            if normalize_string(division["namePoliticalDivisionDefinition"]) == "Poblado" or normalize_string(division["namePoliticalDivisionDefinition"]) =="Municipio"
        }
        LIST_ptOccupation_dict = {
            ocupacion["Name"]: ocupacion["Id"]
            for ocupacion in occupations
        }
        offices_dict = {
        normalize_string(office["nameOffice"]): office["idOffice"]
        for office in offices
        }

        # Obtener ID del tipo de documento
        id_documento = next(
            (
                str(doc["Id"])
                for doc in type_documents
                if doc["Code"] == paciente_data["TIPODOCUMENTO"]
            ),
            "",
        )

        # Obtener ID del sexo al nacer
        id_sexo = next(
            (
                str(sexo["Id"])
                for sexo in administrative_sexes
                if sexo["Code"] == paciente_data["SEXONACER"]
            ),
            "",
        )

        # Obtener ID del estado civil
        id_marital = next(
            (
                str(marital["Id"])
                for marital in marital_statuses
                if map_marital_status(paciente_data["ESTADOCIVIL"])
                == marital["Name"]
            ),
            "",
        )

        # Obtener ID del nivel escolar
        id_scholarship = next(
            (
                str(scholarship["Id"])
                for scholarship in scholarships
                if map_scholarship(paciente_data["NIVELESCOLAR"])
                == scholarship["Name"]
            ),
            "",
        )

        # Obtener ID de la ocupación
        id_occupation = ""
        if paciente_data["OCUPACION"] != "":
            ocupacion_str = str(paciente_data["OCUPACION"]).split(".")[0]
            ocupacionExcel = map_ocupacion(ocupacion_str)
            id_occupation = str(LIST_ptOccupation_dict.get(str(ocupacionExcel), ""))

        # Obtener ID de la religión
        descripcion_mapeada = map_religion(paciente_data["RELIGION"])
        id_religion = next(
            (
                str(religion["Id"])
                for religion in religions
                if normalize_string(religion["Name"]) == descripcion_mapeada
            ),
            "",
        )

        # Obtener ID del proveedor de cuidado
        id_care_provider = next(
            (
                str(proveedor_cuidado["Id"])
                for proveedor_cuidado in care_providers
                if paciente_data["ASEGURADOR"]
                == normalize_string(proveedor_cuidado["Name"])
            ),
            "",
        )

        # Obtener ID de la zona de residencia
        id_zone_residence = next(
            (
                str(Zona["Id"])
                for Zona in zones_residence
                if "ZONA " + paciente_data["ZONA"] == normalize_string(Zona["Name"])
            ),
            "",
        )

        # Obtener ID de ciudades, país, barrio, etc.
        id_birth_place = str(
            ptPoliticalDivision_dict.get(paciente_data["LUGARNACIMIENTO"], "")
        )
        #print(ptPoliticalDivision_HomeAddress.get(normalize_string(paciente_data["CIUDAD"]), ""))
        
        """idHomeAddressPlace = str(
            ptPoliticalDivision_dict.get(normalize_string(paciente_data["CIUDAD"]), "")#["SEDEASIGNACION"], "")
        )"""
        id_office = str(
            offices_dict.get("CLINICOS IPS SEDE "+ paciente_data["SEDEASIGNACION"], "")
        )
        #print("Entra: ",paciente_data["SEDEASIGNACION"],"id_office: ", id_office)

        # Construir el cuerpo del request para el paciente
        paciente_body = {
            "keyWS": KEY_GOMEDISYS_PROD,
            "idDocumentType": id_documento,
            "documentNumber": str(paciente_data["DOCUMENTO"]),
            "firstGivenName": paciente_data["PRIMERNOMBRE"],
            "secondGivenName": paciente_data.get("SEGUNDONOMBRE", ""),
            "firstFamilyName": paciente_data["PRIMERAPELLIDO"],
            "secondFamilyName": paciente_data.get("SEGUNDOAPELLIDO", ""),
            "idAdministrativeSex": id_sexo,
            #"idGenderIdentity": "3028",
            "dateBirth": paciente_data["FECHANACIMIENTO"],
            "idBirthPlace": id_birth_place,
            "idMaritalStatus": id_marital,
            "idScholarship": id_scholarship,
            "idOccupation": id_occupation,
            "idReligion": id_religion,
            "idOffice": id_office,
            "telecom": str(paciente_data.get("FIJO", "")).split(".")[0] or str(paciente_data.get("CELULAR", "")).split(".")[0],
            "homeAddress": paciente_data.get("DIRECCIONCASA", "")+" "+ paciente_data.get("COMPLEMENTODIRECCION", ""),
            "idHomeAddressPlace": paciente_data["CIUDAD"],#idHomeAddressPlace
            "email": paciente_data.get("EMAIL", ""),
            "isSMSEnable": "1",
            "isEmailEnable": "1" if paciente_data.get("EMAIL") else "0",
            "idZone": id_zone_residence
            #"idCareProvider": id_care_provider,
        }
        #body_request.append(paciente_body)

        return paciente_body

    except Exception as e:
        # Imprimir el mensaje de error
        print(f"Error en createBodyRequest_controller.py: {e}")

        # Obtener la información del traceback
        traceback_info = traceback.extract_tb(sys.exc_info()[2])

        # Iterar sobre los marcos de pila
        for tb in traceback_info:
            filename, lineno, funcname, line = tb
            print(
                f"Archivo: {filename}, Línea: {lineno}, Función: {funcname}, Código: {line}"
            )

def map_marital_status(codigo):
    # Usar el metodo del diccionario para que sea mas rapido buscar en los diccionarios o JSON´s
    switch = {
        "A": "Separado",
        "B": "Soltero",
        "C": "Uni\u00f3n libre",
        "D": "Divorciado",
        "E": "Legalmente Separado",
        "M": "Casado",
        "W": "Viudo/a",
        "T": "No reportado",
        "U": "Desconocido",
    }
    return switch.get(codigo, "Desconocido")


def map_scholarship(codigo):
    switch = {
        1: "Preescolar",
        2: "B\u00e1sica Primaria",
        3: "B\u00e1sica Secundaria (Bachillerato B\u00e1sico)",
        4: "Media Acad\u00e9mica o Cl\u00e1sica (Bachillerato B\u00e1sico)",
        5: "Media T\u00e9cnica (Bachillerato T\u00e9cnico)",
        6: "Normalista",
        7: "T\u00e9cnica Profesional",
        8: "Tecnol\u00f3gica",
        9: "Profesional",
        10: "Especializaci\u00f3n",
        11: "Maestr\u00eda",
        12: "Doctorado",
        13: "Ninguno",
    }
    return switch.get(codigo, "Ninguno")


def map_religion(codigo):
    religiones = {
        "NOE": "No religioso",
        "OTH": "Otros",
        "ADV": "Adventista",
        "AGN": "Agnóstico",
        "ATE": "Ateo",
        "BAU": "Bautista",
        "CAO": "Caodaísmo",
        "CAT": "Católico",
        "CIE": "Cienciología",
        "CRI": "Cristiano",
        "ESP": "Espiritualista",
        "EVA": "Evangélico",
        "HIN": "Hindú",
        "ASK": "Askcon",
        "JAI": "Jainismo",
        "JUD": "Judío",
        "MET": "Metodista",
        "MOR": "Mormón",
        "MUS": "Musulmán",
        "ORT": "Ortodoxo",
        "PEN": "Pentecostés",
        "PRO": "Protestante",
        "QUA": "Quaquero",
        "SIJ": "Sijista",
        "SIN": "Zintoísmo",
        "TAO": "Taoísmo",
        "TES": "Testigo de Jehová",
        "WIC": "Wiccan",
    }

    resultado = normalize_string(
        religiones.get(codigo, "No se encontró ninguna coincidencia")
    )
    return resultado


def map_ocupacion(codigo):
    """if codigo != "":  # and codigo is not None
    print("Codigo recibido: ", codigo)"""
    ocupaciones = {
        "1110": "Miembros del poder ejecutivo y de los cuerpos legislativos",
        "1121": "Directores generales, de empresas o entidades de la administración pública",
        "1122": "Directores de regionales, sucursales, oficinas y afines de la administración pública",
        "1110": "Miembros del poder ejecutivo y de los cuerpos legislativos",
        "1121": "Directores generales, de empresas o entidades de la administración pública",
        "1122": "Directores de regionales, sucursales, oficinas y afines de la administración pública",
        "1130": "Jefes de comunidades indígenas, etnias especiales y afines",
        "1141": "Dirigentes y administradores de partidos político",
        "1142": "Dirigentes y administradores de organizaciones de empleadores, de trabajadores y de otras de interés socioeconómico",
        "1143": "Dirigentes y administradores de organizaciones humanitarias y de otras organizaciones especializadas",
        "1211": "Directores y gerentes generales de empresas privadas",
        "1212": "Directores de regionales, sucursales, oficinas y afines de empresas privadas",
        "1311": "Directores de departamentos de producción y operaciones en agricultura, caza, silvicultura y pesca",
        "1312": "Directores de departamentos de producción y operaciones en industrias manufactureras y extractivas",
        "1313": "Directores de departamentos de producción y operaciones en construcción y obras públicas",
        "1314": "Directores de departamentos de producción y operaciones en comercio mayorista y minorista",
        "1315": "Directores de departamentos de producción y operaciones en restaurantes, hoteles y afines",
        "1316": "Directores de departamentos de producción y operaciones en transporte, almacenamiento y comunicaciones",
        "1317": "Directores de departamentos de producción y operaciones en empresas de intermediación financiera y servicios a empresas",
        "1318": "Directores de departamentos de producción y operaciones en servicios de salud, educación y recreación",
        "1319": "Directores de departamentos de producción y operaciones, no clasificados bajo otros epígrafes",
        "1321": "Directores de departamentos financieros y administrativos",
        "1322": "Directores de departamentos de personal y de relaciones laborales",
        "1323": "Directores de departamentos de ventas y comercialización",
        "1324": "Directores de departamentos de publicidad y de relaciones públicas",
        "1325": "Directores de departamentos de abastecimiento y distribución",
        "1326": "Directores de departamentos de servicios de informática",
        "1327": "Directores de departamentos de investigaciones y desarrollo",
        "1329": "Otros directores de departamentos, no clasificados bajo otros epígrafes",
        "1411": "Coordinadores y supervisores financieros y administrativos",
        "1412": "Coordinadores y supervisores de ventas y comercialización",
        "1413": "Coordinadores y supervisores de publicidad, información, relaciones públicas y servicio al cliente",
        "1414": "Coordinadores y supervisores de almacenamiento, abastecimiento y distribución",
        "1415": "Coordinadores y supervisores de informática, investigación y desarrollo",
        "1416": "Coordinadores y supervisores de servicios sociales, educación y salud",
        "1419": "Otros coordinadores y supervisores en mandos medios de empresas públicas y privadas, no clasificados bajo otros epígrafes",
        "1421": "Coordinadores y supervisores de producción y operaciones en aprovechamiento agrícola, pecuario y silvícola",
        "1422": "Coordinadores y supervisores de producción y operaciones en explotación procesamiento y transporte de minerales, petroleo y gas",
        "1423": "Coordinadores y supervisores de producción y operaciones en procesamiento, fabricación y ensamble",
        "1424": "Coordinadores y supervisores de producción y operaciones en construcción y obras públicas",
        "1425": "Coordinadores y supervisores de producción y operaciones en instalación, mantenimiento y reparación mecánica, electrica y electrónica",
        "1426": "Coordinadores y supervisores de producción y operaciones en restaurantes, hotéles hospitales y afines",
        "1427": "Coordinadores y supervisores de producción y operaciones en transporte y comunicaciones",
        "1428": "Coordinadores y supervisores de producción y operaciones en cuidados personales, limpieza y servicios similares",
        "1429": "Coordinadores y supervisores en mandos medios de producción y operaciones en empresas públicas y privadas, no clasificados bajo otros epígrafes",
        "2111": "Físicos y astrónomos",
        "2112": "Meteorólogos",
        "2113": "Químicos y afines",
        "2114": "Geólogos y geofísicos",
        "2121": "Matemáticos y actuarios",
        "2122": "Estadísticos",
        "2130": "Profesionales de la informática",
        "2141": "Arquitectos y urbanistas",
        "2142": "Ingenieros civiles, ingenieros de transporte y afines",
        "2143": "Ingenieros eléctricos, ingenieros electrónicos de telecomunicaciones y afines",
        "2144": "Ingenieros mecánicos",
        "2145": "Ingenieros industriales y afines",
        "2146": "Ingenieros químicos y afines",
        "2147": "Ingenieros de minas, ingenieros metalúrgicos y afines",
        "2148": "Ingenieros catastrales, ingenieros geógrafos y afines",
        "2149": "Arquitectos, ingenieros y afines, no clasificados bajo otros epígrafes",
        "2211": "Biólogos, botánicos, zoólogos y afines",
        "2212": "Especialistas en patología y afines",
        "2213": "Agrónomos y afines",
        "2221": "Médicos",
        "2222": "Odontólogos",
        "2223": "Médicos veterinarios y zootecnistas",
        "2224": "Optómetras",
        "2225": "Fonoaudíologos, fisioterapeutas y afines",
        "2226": "Enfermeros(as) profesionales",
        "2227": "Nutricionistas y dietistas",
        "2229": "Médicos, profesionales en ciencias de la salud y afines, no clasificados bajo otros epígrafes",
        "2311": "Profesores de universidades y otros establecimientos de educación superior",
        "2312": "Profesores de educación secundaria",
        "2313": "Profesores de educación primaria",
        "2314": "Profesores de educación preescolar",
        "2320": "Profesores e instructores de educación especial",
        "2331": "Especialistas en métodos pedagógicos y material didáctico",
        "2332": "Inspectores de la educación",
        "2333": "Consejeros educativos",
        "2339": "Profesionales de la educación, no clasificados bajo otros epígrafes",
        "2411": "Contadores",
        "2412": "Especialistas en políticas, servicios de personal y afines",
        "2413": "Analistas y agentes financieros",
        "2419": "Especialistas en organización, administración de empresas, análisis financiero y afines, no clasificados bajo otros epígrafes",
        "2421": "Abogados",
        "2422": "Jueces",
        "2429": "Profesionales del derecho, no clasificados bajo otros epígrafes",
        "2431": "Catalogadores de piezas de museos, archivos y afines",
        "2432": "Bibliotecarios, documentalistas y afines",
        "2441": "Economistas",
        "2442": "Sociólogos, antropólogos y afines",
        "2443": "Filósofos, historiadores y especialistas en ciencias políticas",
        "2444": "Filólogos, traductores e intérpretes",
        "2445": "Psicólogos",
        "2446": "Trabajadores sociales y afines",
        "2449": "Especialistas en ciencias economicas sociales y humanas, no clasificados bajo otros epígrafes",
        "2451": "Escritores, periodistas y afines",
        "2452": "Escultores, pintores y afines",
        "2453": "Compositores, músicos y cantantes",
        "2454": "Coreógrafos y bailarines",
        "2455": "Actores y directores de cine, radio, teatro, televisión y afines",
        "2460": "Sacerdotes y religiosos de distintas doctrinas",
        "3111": "Técnicos, postsecundarios no universitarios en ciencias físicas, químicas y afines",
        "3112": "Técnicos, postsecundarios no universitarios en ingeniería civil, arquitectura, agrimensores y afines",
        "3113": "Electrotécnicos",
        "3114": "Técnicos y postsecundarios no universitarios en electrónica y telecomunicaciones",
        "3115": "Técnicos y postsecundarios no universitarios en mecánica y construcción mecánica",
        "3116": "Técnicos y postsecundarios no universitarios en ingeniería industrial y química industrial",
        "3117": "Técnicos y postsecundarios no universitarios en ingeniería de minas y metalurgia",
        "3118": "Delineantes y dibujantes técnicos",
        "3119": "Técnicos y postsecundarios no universitarios en ciencias físicas, químicas e ingenierías, no clasificados bajo otros epígrafes",
        "3121": "Analistas de sistemas informáticos",
        "3122": "Técnicos en programación informática",
        "3123": "Técnicos en control de equipos informáticos",
        "3124": "Técnicos en control de robots industriales",
        "3131": "Fotógrafos y operadores de equipos de grabación de imagen y sonido",
        "3132": "Operadores de equipos de radiodifusión, televisión y telecomunicaciones",
        "3133": "Operadores de aparatos de diagnóstico y tratamiento médicos",
        "3139": "Operadores de equipos ópticos y electrónicos, no clasificados bajo otros epígrafes",
        "3141": "Oficiales maquinistas",
        "3142": "Capitanes, oficiales de cubierta y prácticos",
        "3143": "Pilotos de aviación y afines",
        "3144": "Controladores de tráfico aéreo y maritimo",
        "3145": "Técnicos en seguridad aeronáutica",
        "3151": "Inspectores de edificios y de prevención e investigación de incendios",
        "3152": "Inspectores de seguridad y salud y control de calidad",
        "3211": "Técnicos en ciencias biológicas y afines",
        "3212": "Técnicos en agronomía, zootecnia y silvicultura",
        "3221": "Practicantes y asistentes médicos",
        "3222": "Higienistas y promotores de salud",
        "3223": "Técnicos en optometría y ópticos",
        "3224": "Técnicos e higienistas dentales",
        "3225": "Técnicos terapeutas, quiroprácticos y afines",
        "3226": "Técnicos y asistentes veterinarios",
        "3227": "Técnicos y asistentes en farmacia",
        "3229": "Técnicos, postsecundarios no universitarios y asistentes de la medicina moderna y la salud (excepto el personal de partería), no clasificados bajo otros epígrafes",
        "3231": "Practicantes de la medicina tradicional",
        "3232": "Curanderos",
        "3233": "Parteras",
        "3311": "Asistentes de enseñanza en educación superior, secundaria y primaria",
        "3312": "Asistentes de enseñanza en educación preescolar",
        "3320": "Asistentes de educación especial",
        "3331": "Instructores de educación vocacional artística y técnica",
        "3332": "Instructores de educación vocacional artesanal",
        "3333": "Instructores medios de transporte y afines",
        "3411": "Agentes de seguros",
        "3412": "Agentes inmobiliarios",
        "3413": "Agentes de viajes",
        "3414": "Representantes comerciales y técnicos de ventas",
        "3415": "Compradores",
        "3416": "Tasadores y subastadores",
        "3419": "Técnicos, postsecundarios no universitarios y asistentes en operaciones comerciales, no clasificados bajo otros epígrafes",
        "3421": "Agentes de compras, intermediarios y consignatarios",
        "3422": "Asistentes de comercio exterior",
        "3423": "Agentes públicos y privados de colocación y contratistas de mano de obra",
        "3429": "Agentes comerciales y corredores, no clasificados bajo otros epígrafes",
        "3431": "Técnicos, postsecundarios no universitarios y asistentes de servicios administrativos y afines",
        "3432": "Técnicos, postsecundarios no universitarios y asistentes del derecho y servicios legales y afines",
        "3433": "Técnicos, postsecundarios no universitarios y asistentes de servicios financieros, contables y afines",
        "3434": "Técnicos, postsecundarios no universitarios y asistentes de servicios estadísticos, matemáticos y afines",
        "3439": "Técnicos, postsecundarios no universitarios y asistentes de servicios de administración, no clasificados bajo otros epígrafes",
        "3441": "Agentes de aduana e inspectores de fronteras",
        "3442": "Funcionarios del fisco",
        "3443": "Funcionarios de servicios de seguridad social",
        "3444": "Funcionarios de servicios de expedición de licencias y permisos",
        "3449": "Agentes de la administración pública en aduanas, impuestos y afines, no clasificados bajo otros epígrafes",
        "3450": "Inspectores de policía y detectives",
        "3460": "Asistentes en trabajo social y comunitario",
        "3471": "Técnicos en diseño y decoradores",
        "3472": "Locutores de radio, televisión y afines",
        "3473": "Músicos, cantantes y bailarines callejeros, de cabaret y afines",
        "3474": "Recreacionistas, payasos, acróbatas, prestidigitadores y afines",
        "3475": "Atletas, deportistas y afines",
        "3476": "Asistentes de cine, teatro, televisión y artes escénicas",
        "3480": "Auxiliares laicos de los cultos",
        "4111": "Mecanógrafos, transcriptores de textos y afines",
        "4112": "Operadores de calculadoras y entrada de datos",
        "4113": "Secretarios (as)",
        "4121": "Auxiliares de contabilidad y cálculo de costos",
        "4122": "Auxiliares de servicios estadísticos y financieros",
        "4123": "Auxiliares administrativos y afines",
        "4131": "Encargados de control de abastecimientos e inventario",
        "4132": "Encargados de servicios de apoyo a la producción",
        "4133": "Encargados de servicios de transporte",
        "4141": "Empleados de bibliotecas y archivos",
        "4142": "Empleados de servicios de correo",
        "4143": "Codificadores de datos, correctores de pruebas de imprenta y afines",
        "4144": "Escribientes públicos y afines",
        "4211": "Cajeros y expendedores de billetes",
        "4212": "Taquilleros",
        "4213": "Receptores de apuestas y afines",
        "4214": "Prestamistas",
        "4215": "Cobradores y afines",
        "4221": "Empleados de servicios de líneas de viajes aéreas, marítimas y terrestres",
        "4222": "Recepcionistas, empleados de información y servicio al cliente",
        "4223": "Empleados telefonistas y de servicios de internet",
        "5111": "Personal de servicio a pasajeros",
        "5112": "Revisores, guardas y cobradores de los servicios de transporte",
        "5113": "Guías",
        "5121": "Cocineros y afines",
        "5122": "Meseros, taberneros y afines",
        "5131": "Niñeras y cuidadoras infantiles",
        "5132": "Auxiliares de enfermería y odontología",
        "5139": "Trabajadores de los cuidados personales y afines, no clasificados bajo otros epígrafes",
        "5141": "Peluqueros, especialistas en tratamientos de belleza y afines",
        "5142": "Acompañantes",
        "5143": "Personal de pompas fúnebres y embalsamadores",
        "5149": "Otros trabajadores de servicios personales a particulares, no clasificados bajo otros epígrafes",
        "5150": "Astrólogos, adivinadores, quirománticos y afines",
        "5211": "Bomberos y rescatistas",
        "5212": "Agentes y policías de tránsito",
        "5213": "Guardianes de prisión",
        "5219": "Personal de los servicios de protección y seguridad, no clasificado bajo otros epígrafes",
        "5310": "Modelos de modas, arte y publicidad",
        "5320": "Vendedores, demostradores de tiendas y almacenes",
        "5330": "Vendedores en quioscos y puestos de mercado",
        "5341": "Vendedores ambulantes",
        "5342": "Vendedores a domicilio y por teléfono",
        "6111": "Agricultores de cultivos transitorios",
        "6112": "Agricultores de cultivos permanentes (plantaciones de árboles y arbustos)",
        "6113": "Trabajadores de huertas, invernaderos, viveros y jardines",
        "6114": "Trabajadores forestales",
        "6115": "Trabajadores agropecuarios",
        "6121": "Criadores de ganado y trabajadores de la cría de animales domésticos diversos",
        "6122": "Avicultores",
        "6123": "Criadores de insectos, apicultores, sericicultores y afines",
        "6129": "Trabajadores pecuarios, ganaderos y afines, no clasificados bajo otros epígrafes",
        "6131": "Criadores de especies acuáticas",
        "6132": "Pescadores",
        "6133": "Cazadores y tramperos",
        "6211": "Obreros y peones agropecuarios de labranza y de invernadero",
        "6212": "Obreros forestales",
        "6213": "Obreros de pesca, caza y trampa",
        "7111": "Mineros y canteros",
        "7112": "Pegadores cargas explosivas",
        "7113": "Tronzadores, labrantes y grabadores de piedra",
        "7211": "Albañiles, mamposteros y afines",
        "7212": "Operarios en cemento armado, enfoscadores y afines",
        "7213": "Carpinteros de armar y de blanco",
        "7219": "Oficiales y operarios de la construcción y afines, no clasificados bajo otros epígrafes",
        "7221": "Techadores",
        "7222": "Parqueteros y colocadores de suelos",
        "7223": "Instaladores de material aislante y de insonorización",
        "7224": "Cristaleros",
        "7225": "Fontaneros e instaladores de tuberías",
        "7226": "Electricistas de obras y afines",
        "7231": "Revocadores",
        "7232": "Pintores, empapeladores y afines",
        "7233": "Limpiadores de fachadas y deshollinadores",
        "7311": "Moldeadores y macheros",
        "7312": "Soldadores y oxicortadores",
        "7313": "Chapistas y caldereros",
        "7314": "Montadores de estructuras metálicas",
        "7315": "Aparejadores y empalmadores de cables",
        "7316": "Pintores, barnizadores y enlacadores de artículos metálicos y afines",
        "7321": "Herreros y forjadores",
        "7322": "Herramentistas y afines",
        "7323": "Pulidores de metales y afiladores de herramientas",
        "7411": "Mecánicos y ajustadores de vehículos de motor",
        "7412": "Mecánicos y ajustadores de motores de avión",
        "7413": "Mecánicos y ajustadores de máquinas agrícolas e industriales",
        "7414": "Mecánicos y ajustadores de máquinas, herramientas",
        "7421": "Mecánicos y ajustadores eléctricos",
        "7422": "Mecánicos, reparadores y ajustadores de aparatos electrónicos",
        "7423": "Instaladores y reparadores de telégrafos, teléfonos y líneas eléctricas",
        "7511": "Mecánicos y reparadores de instrumentos de precisión",
        "7512": "Fabricantes y afinadores de instrumentos musicales",
        "7521": "Cajistas, tipógrafos y afines",
        "7522": "Estereotipistas y galvanotipistas",
        "7523": "Grabadores de imprenta y fotograbadores",
        "7524": "Operarios de la fotografía y afines",
        "7525": "Encuadernadores y afines",
        "7526": "Impresores de serigrafía y estampadores a la plancha y en textiles",
        "7611": "Alfareros y afines (barro, arcilla y abrasivos)",
        "7612": "Sopladores, modeladores, laminadores, cortadores y pulidores de vidrio",
        "7613": "Grabadores de vidrio",
        "7614": "Pintores decoradores de vidrio, cerámica y otros materiales",
        "7621": "Cesteros, bruceros y afines",
        "7622": "Artesanos de la madera y materiales similares",
        "7631": "Artesanos de los tejidos, el cuero y materiales similares",
        "7632": "Bordadores y afines",
        "7641": "Joyeros, orfebres y plateros",
        "7642": "Floristas y arreglistas florales",
        "7649": "Otros artesanos, no clasificados bajo otros epígrafes",
        "7711": "Carniceros, pescaderos y afines",
        "7712": "Panaderos, pasteleros y confiteros",
        "7713": "Operarios de la elaboración de productos lácteos",
        "7714": "Operarios de la conservación de frutas, legumbres, verduras y afines",
        "7715": "Catadores y clasificadores de alimentos y bebidas",
        "7716": "Preparadores y elaboradores de tabaco y sus productos",
        "7721": "Preparadores de fibras",
        "7722": "Tejedores con telares o de tejidos de punto y afines",
        "7723": "Sastres, modistos, costureros, sombrereros y afines",
        "7724": "Peleteros y afines",
        "7725": "Tapiceros, colchoneros y afines",
        "7731": "Apelambradores, pellejeros y curtidores",
        "7732": "Zapateros y afines",
        "7741": "Operarios del tratamiento de la madera",
        "7742": "Ebanistas y afines",
        "7743": "Ajustadores y operadores de máquinas de labrar madera",
        "8111": "Operadores de instalaciones mineras",
        "8112": "Operadores de instalaciones de procesamiento de minerales y rocas",
        "8113": "Perforadores y sondistas de pozos y afines",
        "8121": "Operadores de hornos de minerales y de hornos de primera fusión de metales",
        "8122": "Operadores de hornos de segunda fusión, máquinas de colar y moldear metales y trenes de laminación",
        "8123": "Operadores de instalaciones de tratamiento térmico de metales",
        "8124": "Operadores de máquinas trefiladoras y estiradoras de metales",
        "8131": "Operadores de mezcladoras y de hornos de vidriería y afines",
        "8132": "Operadores de mezcladoras y de hornos de cerámica y afines",
        "8139": "Operadores de instalaciones de vidriería, cerámica y afines, no clasificados bajo otros epígrafes",
        "8141": "Operadores de instalaciones de procesamiento de la madera",
        "8142": "Operadores de instalaciones para la preparación de pasta o pulpa para papel",
        "8143": "Operadores de instalaciones para la fabricación de papel",
        "8151": "Operadores de instalaciones quebrantadoras, trituradoras y mezcladoras de sustancias químicas",
        "8152": "Operadores de instalaciones de tratamiento químico térmico",
        "8153": "Operadores de equipos de filtración y separación de sustancias químicas",
        "8154": "Operadores de equipos de destilación y de reacción química (excepto petróleo y gas natural)",
        "8155": "Operadores de instalaciones de refinación de petróleo y gas natural",
        "8159": "Operadores de instalaciones de tratamientos químicos no clasificados bajo otros epígrafes",
        "8161": "Operadores de instalaciones de producción de energía",
        "8162": "Operadores de máquinas de vapor y calderas",
        "8163": "Operadores de incineradores",
        "8164": "Operadores de instalaciones de tratamiento de agua y afines",
        "8165": "Operadores de instalaciones de refrigeración, calefacción y ventilación",
        "8170": "Operadores de cadenas de montaje automatizadas e instalaciones mecánicas y de robots industriales",
        "8211": "Operadores de máquinas herramientas y afines",
        "8212": "Operadores de máquinas para fabricar productos de cemento y otros productos minerales",
        "8221": "Operadores de máquinas para fabricar productos farmacéuticos y cosméticos",
        "8222": "Operadores de máquinas para fabricar municiones y explosivos",
        "8223": "Operadores de máquinas pulidoras, galvanizadoras y recubridoras de metales",
        "8229": "Operadores de máquinas para fabricar productos químicos, no clasificados bajo otros epígrafes",
        "8231": "Operadores de máquinas para fabricar productos de caucho",
        "8232": "Operadores de máquinas para fabricar productos de plástico",
        "8240": "Operadores de máquinas para fabricar productos de madera",
        "8251": "Operadores de máquinas de imprenta, reproducción fotográfica y afines",
        "8252": "Operadores de máquinas de encuadernación",
        "8253": "Operadores de máquinas para fabricar productos de papel y afines",
        "8261": "Operadores de máquinas de preparación de fibras, hilado y devanado",
        "8262": "Operadores de telares y otras máquinas tejedoras",
        "8263": "Operadores de máquinas para coser",
        "8264": "Operadores de máquinas de blanqueo, teñido y tintura",
        "8265": "Operadores de máquinas de tratamiento de pieles y cueros",
        "8266": "Operadores de máquinas para la fabricación de calzado y afines",
        "8267": "Patronistas, cortadores de tela, cuero y afines",
        "8269": "Operadores de máquinas para fabricar productos textiles y artículos de piel y cuero, no clasificados bajo otros epígrafes",
        "8271": "Operadores de máquinas para procesar carne, pescado y mariscos",
        "8272": "Operadores de máquinas para elaborar productos lácteos",
        "8273": "Operadores de máquinas para moler cereales y especias",
        "8274": "Operadores de máquinas para procesar cereales, productos de panadería, repostería y confitería",
        "8275": "Operadores de máquinas para procesar frutos húmedos, secos y hortalizas",
        "8276": "Operadores de máquinas para fabricar azúcares",
        "8277": "Operadores de máquinas para elaborar té, café y cacao",
        "8278": "Operadores de máquinas para elaborar cerveza, vinos y otras bebidas",
        "8279": "Operadores de máquinas para elaborar productos del tabaco",
        "8281": "Ensambladores de mecanismos y elementos mecánicos de máquinas",
        "8282": "Ensambladores de equipos eléctricos",
        "8283": "Ensambladores de equipos electrónicos",
        "8284": "Ensambladores de productos metálicos, de caucho y plástico",
        "8285": "Ensambladores de productos de madera y materiales afines",
        "8286": "Ensambladores de productos de cartón, textiles y materiales afines",
        "8290": "Otros operadores de máquinas y ensambladores",
        "8311": "Maquinistas de vehículos por riel",
        "8312": "Guardafrenos, guardagujas y agentes de maniobras",
        "8321": "Conductores de camionetas y vehículos livianos",
        "8322": "Conductores de taxis",
        "8323": "Conductores de buses, microbuses y colectivos",
        "8324": "Conductores de camiones y vehículos pesados",
        "8331": "Operadores de maquinaria agrícola y forestal motorizada",
        "8332": "Operadores de máquinas de movimiento de tierras, construcción vías y afines",
        "8333": "Operadores de grúas, de aparatos elevadores y afines",
        "8334": "Operadores de carretillas elevadoras",
        "8340": "Marineros de cubierta y afines",
        "9111": "Ayudante de taller, mecánica, vehículos de motor y afines",
        "9112": "Ayudantes en reparación y mecánica en general (excepto vehículos de motor)",
        "9120": "Limpiabotas y otros trabajadores callejeros",
        "9131": "Mensajeros, porteadores y repartidores",
        "9132": "Porteros, conserjes y afines",
        "9133": "Vigilantes y celadores",
        "9134": "Recolectores y surtidores de aparatos automáticos",
        "9135": "Lectores de medidores",
        "9141": "Recolectores de basura",
        "9142": "Barrenderos y afines",
        "9143": "Recolectores de material reciclable",
        "9210": "Personal doméstico",
        "9221": "Aseadores y fumigadores de oficinas, hoteles y otros establecimientos",
        "9222": "Lavanderos y planchadores manuales",
        "9223": "Lavadores de vehículos, ventanas y afines",
        "9311": "Obreros de minas y canteras",
        "9312": "Obreros de obras públicas y mantenimiento: carreteras, presas y obras similares",
        "9313": "Obreros de la construcción de edificios",
        "9321": "Obreros de ensamble",
        "9322": "Embaladores manuales y otros obreros de la industria manufacturera",
        "9331": "Conductores de vehículos accionados a pedal o a brazo",
        "9332": "Conductores de vehículos de tracción animal",
        "9333": "Obreros de carga",
    }
    """ if ocupaciones.get(codigo, "Ocupación no encontrada") == "Ocupación no encontrada":
        hola = "Ocupación no encontrada"
    else:
        print(ocupaciones.get(codigo, "Ocupación no encontrada")) """
    return ocupaciones.get(codigo, "Ocupación no encontrada")
