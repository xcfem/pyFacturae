# -*- coding: utf-8 -*-

import xml_tools as xt;

class FacturaeParty(object):
    '''
     Facturae Party

    Represents a party, which is an entity defined by Facturae that can be
    the seller or the buyer of an invoice.
    '''

    isLegalEntity= True; # By default is a company and not a person
    taxNumber= None
    name= None

    # This block is only used for legal entities
    book= None                        # "Libro"
    registerOfCompaniesLocation= None # "Registro mercantil"
    sheet= None                       # "Hoja"
    folio= None                       # "Folio"
    section= None                     # "Sección"
    volume= None                      # "Tomo"

    # This block is only required for individuals
    firstSurname= None
    lastSurname= None

    address= None
    postCode= None
    town= None
    province= None
    countryCode= "ESP";

    email= None
    phone= None
    fax= None
    website= None

    contactPeople= None
    cnoCnae= None
    ineTownCode= None
    centres= list();


    def __init__(properties:dict):
        '''
           Construct

           :param properties: Party properties as an array
        '''
        self.properties= dict()
        for key in properties:
            value= properties[key]
            self.properties[key]= value
        if(self.properties['merchantRegister']!= None):
            self.registerOfCompaniesLocation= self.merchantRegister


    def getXML(schema):
        '''
           Get XML

           :param  schema: Facturae schema version
           :return Entity as Facturae XML
        '''
        tools= xt.XmlTools()

        # Add tax identification
        charLegalEntity= 'F'
        if(this.properties['isLegalEntity']):
            charLegalEntity= 'J'
        xml= '<TaxIdentification>'
        xml+= '<PersonTypeCode>' + charLegalEntity + '</PersonTypeCode>'
        xml+= '<ResidenceTypeCode>R</ResidenceTypeCode>'
        xml+= '<TaxIdentificationNumber>' + tools.escape(this.taxNumber) + '</TaxIdentificationNumber>'
        xml+= '</TaxIdentification>'

        # Add administrative centres
        if(len(this.centres) > 0):
          xml+= '<AdministrativeCentres>'
          for centre in self.centres:
            xml+= '<AdministrativeCentre>'
            xml+= '<CentreCode>' + centre.code + '</CentreCode>'
            xml+= '<RoleTypeCode>' + centre.role + '</RoleTypeCode>'
            xml+= '<Name>' + tools.escape(centre.name) + '</Name>'
            if(centre.firstSurname!=None):
                xml+= '<FirstSurname>' + tools.escape(centre.firstSurname) + '</FirstSurname>'
            if(centre.lastSurname!=None):
                xml+= '<SecondSurname>' + tools.escape(centre.lastSurname) + '</SecondSurname>'

            # Get centre address, else use fallback
            addressTarget= centre
            for field in ['address', 'postCode', 'town', 'province', 'countryCode']:
                value= centre[field]
                if(value==None):
                    addressTarget= self
                    break

            if(addressTarget.countryCode == "ESP"):
              xml+= '<AddressInSpain>'
              xml+= '<Address>'+tools.escape(addressTarget.address)+ '</Address>'
              xml+= '<PostCode>' + addressTarget.postCode + '</PostCode>'
              xml+= '<Town>' + tools.escape(addressTarget.town) + '</Town>'
              xml+= '<Province>' + tools.escape(addressTarget.province) + '</Province>'
              xml+= '<CountryCode>' + addressTarget.countryCode + '</CountryCode>'
              xml+= '</AddressInSpain>'
            else:
              xml+= '<OverseasAddress>'
              xml+= '<Address>' + tools.escape(addressTarget.address) + '</Address>'
              xml+= '<PostCodeAndTown>' + addressTarget.postCode + ' ' + tools.escape(addressTarget.town) + '</PostCodeAndTown>'
              xml+= '<Province>' + tools.escape(addressTarget.province) + '</Province>'
              xml+= '<CountryCode>' + addressTarget.countryCode + '</CountryCode>'
              xml+= '</OverseasAddress>'

            if(centre.description!=None):
                xml+= '<CentreDescription>' + tools.escape(centre.description) + '</CentreDescription>'
            xml+= '</AdministrativeCentre>'
          xml+= '</AdministrativeCentres>'

        # Add custom block (either `LegalEntity` or `Individual`)
        legalEntityBlock= '<LegalEntity>'
        if(not self.isLegalEntity):
            legalEntityBlock= '<Individual>'
        xml+= legalEntityBlock 

        # Add data exclusive to `LegalEntity`
        if(self.isLegalEntity):
            xml+= '<CorporateName>' + tools.escape(self.name) + '</CorporateName>'
            fields= ["book", "registerOfCompaniesLocation", "sheet", "folio",
            "section", "volume"]

            nonEmptyFields= list()
            for fieldName in fields:
              if(self.properties[fieldName]!= None):
                  nonEmptyFields.append(fieldName)

            if(len(nonEmptyFields) > 0):
                xml+= '<RegistrationData>'
                for fieldName in nonEmptyFields:
                    tag= ucfirst(fieldName)
                    xml+= "<tag>" + self.properties[fieldName] + "</tag>"
                xml+= '</RegistrationData>'

        # Add data exclusive to `Individual`
        if(not self.isLegalEntity):
          xml+= '<Name>' + tools.escape(self.name) + '</Name>'
          xml+= '<FirstSurname>' + tools.escape(self.firstSurname) + '</FirstSurname>'
          xml+= '<SecondSurname>' + tools.escape(self.lastSurname) + '</SecondSurname>'

        # Add address
        if(self.countryCode == "ESP"):
            xml+= '<AddressInSpain>' +\
              '<Address>' + tools.escape(self.address) + '</Address>' +\
              '<PostCode>' + self.postCode + '</PostCode>' +\
              '<Town>' + tools.escape(self.town) + '</Town>' +\
              '<Province>' + tools.escape(self.province) + '</Province>' +\
              '<CountryCode>' + self.countryCode + '</CountryCode>' +\
              '</AddressInSpain>'
        else:
            xml+= '<OverseasAddress>' +\
              '<Address>' + tools.escape(self.address) + '</Address>' +\
              '<PostCodeAndTown>' + self.postCode + ' ' + tools.escape(self.town) + '</PostCodeAndTown>' +\
              '<Province>' + tools.escape(self.province) + '</Province>' +\
              '<CountryCode>' + self.countryCode + '</CountryCode>' +\
              '</OverseasAddress>'
              
        # Add contact details
        xml+= self.getContactDetailsXML()

        # Close custom block
        legalEntityBlock= '</LegalEntity>'
        if(not self.isLegalEntity):
            legalEntityBlock= '</Individual>'
        xml+= legalEntityBlock

        # Return data
        return xml

    def getContactDetailsXML():
        '''
           Get contact details XML

           :return string Contact details XML
        '''
        tools= XmlTools()
        contactFields= {"phone":"Telephone",
          "fax":"TeleFax",
          "website":"WebAddress",
          "email":"ElectronicMail",
          "contactPeople":"ContactPersons",
          "cnoCnae":"CnoCnae",
          "ineTownCode":"INETownCode"}

        # Validate attributes
        hasDetails= False
        for field in contactFields:
          if(self.field!=None):
              hasDetails= True
              break
          
        if(not hasDetails):
            return ""
        else:
            # Add fields
            xml= '<ContactDetails>'
            for field in contactFields:# as field=>xmlName):
                value= self.properties[field]
                if(value!=None):
                  xml+= "<xmlName>" + tools.escape(value) + "</xmlName>"
            xml+= '</ContactDetails>'

        return xml




