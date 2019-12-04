from functools import reduce

def calculator(st):
    try:
        st = st.lower().replace(' ', '')
        parts = st.split('+')
        
        for i in range(len(parts)):
            if '-' in parts[i]:
                parts[i] = parts[i].split('-')
            parts[i] = precalc(parts[i])
        result = sum(parts)
    except ValueError:
        result = 'Smth not understand'
    except ZeroDivisionError:
        result = 'Division by zero'
    return result
   
    
def preprecalc(st):
    if '*' in st:
        return reduce(lambda x,y: x*y, map(preprecalc, st.split('*')))
    elif '/' in st:
        return reduce(lambda x,y: x/y, map(preprecalc, st.split('/')))
    else:
        return float(st)

         
def precalc(part):
    if type(part) is str:      
        return preprecalc(part)
    elif type(part) is list:
        return reduce(lambda x,y: x-y, map(preprecalc, part))
    else:
        raise ValueError('Bad type.')
   


