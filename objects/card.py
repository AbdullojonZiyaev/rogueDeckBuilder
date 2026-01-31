class Card:
    
    """
    name = имя
    power = мощь
    cost = стоимость
    WP = winning points(ПО)
    ability = свойство (что делает?)
    """
    def __init__ (self, card_index, name, power, cost, WP, ability):
        self.card_index = card_index
        self.name = name
        self.power = power
        self.cost = cost
        self.WP = WP
        self.ability = ability
    
    def getCard (self):
        return self.card_index

    def getPower (self):
        return self.power
    
    def getName (self):
        return self.name
    
    def getCost (self):
        return self.cost
    
    def getWP (self):
        return self.WP
    
    def getAbility (self):
        return self.ability

