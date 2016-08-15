from vcc_mod import *


def main(argv):
	if len(sys.argv)<5:
		print "Error: Need four arguments"
		print "       Virtual Chassis IP, Cluster Name, Cluster ID, Starting FPC Number for this Cluster\n"
	else:
			v2fmain(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])


if __name__ == "__main__":
    	main(sys.argv)
