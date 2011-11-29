import select
import sys
import pybonjour
from netgrowl import *

regtype  = "_growl._tcp"
timeout  = 1
title = "Reach" if len(sys.argv) < 2 else sys.argv[1]
description = "For the Stars!" if len(sys.argv) < 3 else sys.argv[2]
password = "reachforthestars"
hosts = []

def growl_test(name, port):
    addr = (name, GROWL_UDP_PORT)
    s = socket(AF_INET, SOCK_DGRAM)
    p = GrowlRegistrationPacket(password=password)
    p.addNotification()
    s.sendto(p.payload(), addr)

    p = GrowlNotificationPacket(priority=-2, password=password, title=title, description=description)
    s.sendto(p.payload(), addr)

def resolve_callback(sdRef, flags, interfaceIndex, errorCode, fullname,
                     hosttarget, port, txtRecord):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
        if not hosttarget in hosts:
            growl_test(hosttarget, port)
            hosts.append(hosttarget)

def browse_callback(sdRef, flags, interfaceIndex, errorCode, serviceName,
                    regtype, replyDomain):
    if errorCode != pybonjour.kDNSServiceErr_NoError:
        return

    if not (flags & pybonjour.kDNSServiceFlagsAdd):
        print 'Service removed'
        return

    resolve_sdRef = pybonjour.DNSServiceResolve(0,
                                                interfaceIndex,
                                                serviceName,
                                                regtype,
                                                replyDomain,
                                                resolve_callback)

    try:
        while not hosts:
            ready = select.select([resolve_sdRef], [], [], timeout)
            if resolve_sdRef not in ready[0]:
                print 'Resolve timed out'
            pybonjour.DNSServiceProcessResult(resolve_sdRef)
    finally:
        resolve_sdRef.close()


browse_sdRef = pybonjour.DNSServiceBrowse(regtype = regtype,
                                          callBack = browse_callback)

try:
    for n in range(0, 3):
        # Only want to notify one host anyways
        if len(hosts) > 0: break
        ready = select.select([browse_sdRef], [], [], timeout)
        if browse_sdRef in ready[0]:
            pybonjour.DNSServiceProcessResult(browse_sdRef)
finally:
    browse_sdRef.close()
