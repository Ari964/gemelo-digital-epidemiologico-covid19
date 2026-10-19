import json

path = 'docs/auditoria_ejecucion_langflow.json'
with open(path, 'r', encoding='utf-8') as f:
    audit = json.load(f)

audit['system_prompt_update'] = {
    'status': 'ACTUALIZADO_AUTOMATICO_CHINO_A_ESPANOL',
    'descripcion': 'El prompt de Agent-EXpSZ fue reconfigurado para traducir automaticamente cualquier frase recibida en caracteres chinos (simplificados o tradicionales) directamente al espanol sin requerir prefijos como traduce al espanol, desglosando traduccion, pinyin y vocabulario.',
    'exported_file': 'docs/flujo_traductor_langflow_exportado.json',
    'credentials_present': False
}

audit['session_runtime_telemetry'] = {
    'docker_service_status': 'OFFLINE_IN_SESSION (daemon named pipe no disponible en sesion de fondo sin entorno grafico activo)',
    'action_for_defense_day': 'Iniciar Docker Desktop en Windows y ejecutar docker compose up -d en C:\\Users\\KRISTEL\\Documents\\langflow\\docker_example. El servicio abrira en http://localhost:7860 con persistencia PostgreSQL.'
}

audit['new_test_sentences_spec'] = [
    {
        'id': 'frase_nueva_1',
        'input_chinese': '流行病学模型显示，早期干预能够显著降低重症监护病房的峰值负荷。',
        'translation_es': 'Los modelos epidemiológicos muestran que la intervención temprana puede reducir significativamente la carga máxima en las unidades de cuidados intensivos.',
        'pinyin': 'Liúxíngbìngxué móxíng xiǎnshì, zǎoqī gānyù nénggòu xiǎnzhù jiàngdī zhòngzhèng jiānhù bìngfáng de fēngzhí fùhè.',
        'vocabulario': [
            {'termino': '流行病学模型 (liúxíngbìngxué móxíng)', 'significado': 'Modelo epidemiológico'},
            {'termino': '早期干预 (zǎoqī gānyù)', 'significado': 'Intervención temprana'},
            {'termino': '显著降低 (xiǎnzhù jiàngdī)', 'significado': 'Reducir significativamente'},
            {'termino': '重症监护病房 (zhòngzhèng jiānhù bìngfáng)', 'significado': 'Unidad de cuidados intensivos (UCI)'},
            {'termino': '峰值负荷 (fēngzhí fùhè)', 'significado': 'Carga máxima / pico de demanda'}
        ]
    },
    {
        'id': 'frase_nueva_2',
        'input_chinese': '在偏远社区，移动医疗队在疾病监测和初级保健中发挥了不可替代的作用。',
        'translation_es': 'En las comunidades remotas, los equipos médicos móviles han desempeñado un papel insustituible en la vigilancia de enfermedades y la atención primaria de salud.',
        'pinyin': 'Zài piānyuǎn shèqū, yídòng yīliáoduì zài jíbìng jiāncè hé chūjí bǎojiàn zhōng fāhuīle bùkě tìdài de zuòyòng.',
        'vocabulario': [
            {'termino': '偏远社区 (piānyuǎn shèqū)', 'significado': 'Comunidades remotas'},
            {'termino': '移动医疗队 (yídòng yīliáoduì)', 'significado': 'Equipos médicos móviles'},
            {'termino': '疾病监测 (jíbìng jiāncè)', 'significado': 'Vigilancia de enfermedades / epidemiológica'},
            {'termino': '初级保健 (chūjí bǎojiàn)', 'significado': 'Atención primaria de salud'},
            {'termino': '不可替代的作用 (bùkě tìdài de zuòyòng)', 'significado': 'Papel insustituible / rol irremplazable'}
        ]
    }
]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(audit, f, indent=2, ensure_ascii=False)
print('Updated auditoria_ejecucion_langflow.json successfully')
