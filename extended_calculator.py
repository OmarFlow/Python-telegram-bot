from functools import reduce

def calculator(user_expression):
    try:
        user_expression = user_expression.lower().replace(' ', '')
        parts = user_expression.split('+')
        
        for part in range(len(parts)):
            
            if '-' in parts[part]:
                parts[part] = parts[part].split('-')
                
            parts[part] = precalc(parts[part])
            
        result = sum(parts)

    except ValueError:
        result = 'Smth not underuser_expressionand'
    except ZeroDivisionError:
        result = 'Division by zero'
    return result
   
    
def preprecalc(part):
    if '*' in part:
        return reduce(lambda x,y: x*y, map(preprecalc, part.split('*')))
    
    elif '/' in part:
        return reduce(lambda x,y: x/y, map(preprecalc, part.split('/')))
    
    return float(part)

         
def precalc(part):
    if type(part) is str:      
        return preprecalc(part)
    
    elif type(part) is list:
        return reduce(lambda x,y: x-y, map(preprecalc, part))
    
    raise ValueError('Bad type.')
   


