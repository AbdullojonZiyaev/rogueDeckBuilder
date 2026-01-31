class Card:
    """
    name = имя
    power = мощь
    cost = стоимость
    WP = winning points(ПО)
    ability = свойство (что делает?)
    """
    def __init__ (self, card_index, name, power, cost, WP, count, card_type, isLegendary, isStart, ability):
        self.card_index = card_index
        self.name = name
        self.power = power
        self.cost = cost
        self.WP = WP
        self.count = count
        self.card_type = card_type
        self.isLegendary = isLegendary
        self.isStart = isStart
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
    
    def getCount(self):
        return self.count
    
    def getCardType(self):
        return self.card_type
    
    def getIsLegendary(self):
        return self.isLegendary
    
    def getIsStart(self):
        return self.isStart
    
    def getAbility (self):
        return self.ability

