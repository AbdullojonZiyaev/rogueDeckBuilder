class Card:
    
    """
    name = имя
    power = мощь
    cost = стоимость
    WP = winning points(ПО)
    ability = свойство (что делает?)
    """
    def __init__ (self, name, power, cost, WP, ability):
        self.name = name
        self.power = power
        self.cost = cost
        self.WP = WP
        self.ability = ability

    def GetPower (self):
        return self.power
    
    def GetName (self):
        return self.name
    
    def GetCost (self):
        return self.cost
    
    def getWP (self):
        return self.WP
    
    def getAbility (self):
        return self.ability

