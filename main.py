from supreme import Supreme

def main(category, name, color, size, checkoutDelay):
    supreme = Supreme(category, name, color, size, checkoutDelay)
    supreme.addToCart(supreme.search())
    supreme.checkOut()

if __name__ == '__main__':
    category = 'jackets'        #category
    name = ''        #item name
    color = ''              #color
    size = 'medium'              #size
    checkoutDelay = None        #delay to avoid possible ghost checkout

    main(category, name, color, size, checkoutDelay)