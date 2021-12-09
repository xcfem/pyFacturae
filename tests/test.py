# -*- coding: utf-8 -*-
'''Test Facturae.'''

import facturae as fe
import facturae_party as fp

fac= fe.Facturae();
fac.setNumber('FAC201804', '123');
fac.setIssueDate('2018-04-01');

fac.setSeller(fp.FacturaeParty({
  "taxNumber" : "A00000000",
  "name"      : "Perico de los Palotes S.A.",
  "address"   : "C/ Falsa, 123",
  "postCode"  : "12345",
  "town"      : "Madrid",
  "province"  : "Madrid"
}));
fac.setBuyer(fp.FacturaeParty({
  "isLegalEntity" : false,
  "taxNumber"     : "00000000A",
  "name"          : "Antonio",
  "firstSurname"  : "García",
  "lastSurname"   : "Pérez",
  "address"       : "Avda. Mayor, 7",
  "postCode"      : "54321",
  "town"          : "Madrid",
  "province"      : "Madrid"
}));

fac.addItem("Lámpara de pie", 20.14, 3, Facturae.TAX_IVA, 21);

fac.sign("certificado.pfx", null, "passphrase");
fac.export("mi-factura.xsig");
