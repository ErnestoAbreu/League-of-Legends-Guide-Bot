from datetime import datetime

class Status:
    def write(self, text: str) -> None:
        file = open('status.log', 'a')
        file.write(str(datetime.now()) + '  ' + text + '\n')
        file.close()

    def transform_description(self, description: str) -> str:
        check_tag = False
        tag = ''
        text = ''
        for c in description:
            if c == '<':
                check_tag = True
                continue

            if c == '>':
                check_tag = False
                if tag == 'li': text += '\n'
                if tag == 'stats': text += '<i>'
                if tag == '/stats': text += '</i>'
                if tag == 'attention': text += '<b>'
                if tag == '/attention': text += '</b>'
                if tag == 'br': text += '\n'
                if tag == 'status': text += '<code>'
                if tag == '/status': text += '</code>'
                if tag == 'passive': text += '<b><i>'
                if tag == '/passive': text += '</i></b>'
                if tag == 'active': text += '<b><i>'
                if tag == '/active': text += '</i></b>'
                if tag == 'rarityMythic': text += '<b><i><u>'
                if tag == '/rarityMythic': text += '</u></i></b>'
                tag = ''
                continue
            
            if check_tag:
                tag += c
            else:
                text += c
        
        return text + '\n'