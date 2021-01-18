#!/usr/bin/python3
import sys
import logging
import datetime
import getopt
import dns.query
import dns.zone

iplist = {''}
domainlist = {''}
subdomainlist = {''}

def main(argv):
    print("hi")
    ipfile = ''
    domainfile = ''
    subdomainfile = ''

    try:
        print(argv)
        if len(argv)!= 6:
            print ('Usage: zonetransfer4.py -i <ipfile> -d <outdomainfileputfile> -s <subdomainfile>')
            sys.exit(2)
        opts, args = getopt.getopt(argv,"i:d:s:",["ifile=","dfile=","sfile="])
        print(opts)
    except getopt.GetoptError:
        print ('test.py -i <ipfile> -d <outdomainfileputfile> -s <subdomainfile>')
        sys.exit(2)
    for opt, arg in opts:
        print(opt)
        if opt in ("-i", "--ifile"):
            ipfile = arg
            with open(ipfile) as f:
                iplist = f.readlines()
                iplist = [x.strip() for x in iplist]
        elif opt in ("-d", "--dfile"):
            domainfile = arg
            with open(domainfile) as f:
                domainlist = f.readlines()
                domainlist = [x.strip() for x in domainlist]
        elif opt in ("-s", "--sfile"):
            subdomainfile = arg
            with open(subdomainfile) as f:
                subdomainlist = f.readlines()
                subdomainlist = [x.strip() for x in subdomainlist]
    print ('Ipfile is {}'.format(ipfile))
    print ('Domainfile is {}'.format(domainfile))
    print ('Subdomainfile is {}'.format(subdomainfile))

    # Reading output_files
    stored_exception=None

    filetime = datetime.datetime.now().strftime("%y%m%d-%H%M%S") #  Timestamp
    script_results = "xfer_summary_" + filetime + ".csv" # Output Filname

    output = open(script_results, "w+") # <- Write the file
    output.write('server,domain,status\n')

    output_files = []
    output_files.append(script_results)

    # Logging Setup
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.DEBUG)
    logger = logging.getLogger("xfr")

    for server in iplist:
        server = server.rstrip()
        for maindomain in domainlist:
            dnszonetransfer(maindomain,server, logger, output)
            for subdomain in subdomainlist:
                domain = subdomain+"."+maindomain
                dnszonetransfer(domain,server, logger, output)
    output.close() # <- Close the file


def dnszonetransfer(domain, server, logger, output):
    try:
        z = dns.zone.from_xfr(dns.query.xfr(server, domain))
        print("I'm here")
        output.write(str(server) + "," + str(domain) + ",xfr_enabled\n")
        logger.info("XFR Enabled: %s - %s", server, domain)
        names = z.nodes.keys()
        names.sort()
        domain_results = server + "_" + domain + "_" + filetime + ".txt" # Output Filname
        domain_output = open(domain_results, "w+") # <- Write the file
        for n in names:
            zonefile_line = z[n].to_text(n)
            logger.debug(zonefile_line)
            domain_output.write(str(zonefile_line) + "\n")
        output_files.append(domain_results)
        domain_output.close()
        if stored_exception:
            sys.exit()
    except KeyboardInterrupt:
        stored_exception=sys.exc_info()
    except:
        logger.critical("Zone Tranfser Failed: %s | %s ", server, domain)
        logger.debug("Exception: %s %s", sys.exc_info()[0], sys.exc_info()[1])
        output.write(str(server) + "," + str(domain) + ",xfr_failed\n")
        logger.info("XFR Failed: %s - %s", server, domain)

if __name__ == "__main__":
    main(sys.argv[1:])
