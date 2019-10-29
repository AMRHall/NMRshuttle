import julaboController
import sys, time

dyneo = julaboController.dyneo()

if sys.argv[1] == 'OFF':
	dyneo.switchOff()
	print('Dyneo off')
	
else:
	dyneo.switchOn()
	time.sleep(1)
	dyneo.setTemp(float(sys.argv[1]))

dyneo.close()
