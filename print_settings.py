import json, os

def show_settings():
    p = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                d = json.load(f)
            km = {'left': 'LMB', 'right': 'RMB', 'middle': 'MMB'}
            keys = ', '.join([km.get(str(k).lower(), str(k).upper()) for k in d.get('keys', [])])
            delay = d.get('delay', 0.02)
            print('Текущие настройки:')
            print('  Кнопка включения: ' + str(d.get('toggle_key', 'F10')))
            print('  Клавиши:          ' + keys)
            print('  Задержка:         ' + str(delay))
        except Exception as e:
            print(f'Ошибка чтения конфигурации: {e}')

if __name__ == '__main__':
    show_settings()
