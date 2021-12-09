# -*- coding: utf-8 -*-
'''Class for creating electronic invoices that comply with the Spanish FacturaE format.

Migrated to Python from: https://github.com/josemmo/Facturae-PHP
'''

__author__= "Luis C. Pérez Tato (LCPT) Ana Ortega (A_OO) "
__copyright__= "Copyright 2015,  LCPT A_OO "
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com ana.Ortega.Ort@gmail.com"

# import josemmo\Facturae\FacturaeTraits\PropertiesTrait;
# import josemmo\Facturae\FacturaeTraits\UtilsTrait;
# import josemmo\Facturae\FacturaeTraits\SignableTrait;
# import josemmo\Facturae\FacturaeTraits\ExportableTrait;

class Facturae(object):
    ''' Class for creating electronic invoices that comply with the Spanish FacturaE format.'''
    VERSION= '1.6.1'
    USER_AGENT= 'FacturaePHP/' + VERSION

    SCHEMA_3_2= '3.2'
    SCHEMA_3_2_1= '3.2.1'
    SCHEMA_3_2_2= '3.2.2'
    SIGN_POLICY_3_1= {'name':'Política de Firma FacturaE v3.1','url':'http://www.facturae.es/politica_de_firma_formato_facturae/politica_de_firma_formato_facturae_v3_1.pdf','digest':'Ohixl6upD6av8N7pEvDABhEL6hM='}

    PAYMENT_CASH= '01'
    PAYMENT_DEBIT= '02'
    PAYMENT_RECEIPT= '03'
    PAYMENT_TRANSFER= '04'
    PAYMENT_ACCEPTED_BILL_OF_EXCHANGE= '05'
    PAYMENT_DOCUMENTARY_CREDIT= '06'
    PAYMENT_CONTRACT_AWARD= '07'
    PAYMENT_BILL_OF_EXCHANGE= '08'
    PAYMENT_TRANSFERABLE_IOU= '09'
    PAYMENT_IOU= '10'
    PAYMENT_CHEQUE= '11'
    PAYMENT_REIMBURSEMENT= '12'
    PAYMENT_SPECIAL= '13'
    PAYMENT_SETOFF= '14'
    PAYMENT_POSTGIRO= '15'
    PAYMENT_CERTIFIED_CHEQUE= '16'
    PAYMENT_BANKERS_DRAFT= '17'
    PAYMENT_CASH_ON_DELIVERY= '18'
    PAYMENT_CARD= '19'

    TAX_IVA= '01'
    TAX_IPSI= '02'
    TAX_IGIC= '03'
    TAX_IRPF= '04'
    TAX_OTHER= '05'
    TAX_ITPAJD= '06'
    TAX_IE= '07'
    TAX_RA= '08'
    TAX_IGTECM= '09'
    TAX_IECDPCAC= '10'
    TAX_IIIMAB= '11'
    TAX_ICIO= '12'
    TAX_IMVDN= '13'
    TAX_IMSN= '14'
    TAX_IMGSN= '15'
    TAX_IMPN= '16'
    TAX_REIVA= '17'
    TAX_REIGIC= '18'
    TAX_REIPSI= '19'
    TAX_IPS= '20'
    TAX_RLEA= '21'
    TAX_IVPEE= '22'
    TAX_IPCNG= '23'
    TAX_IACNG= '24'
    TAX_IDEC= '25'
    TAX_ILTCAC= '26'
    TAX_IGFEI= '27'
    TAX_IRNR= '28'
    TAX_ISS= '29'

    UNIT_DEFAULT= '01'
    UNIT_HOURS= '02'
    UNIT_KILOGRAMS= '03'
    UNIT_LITERS= '04'
    UNIT_OTHER= '05'
    UNIT_BOXES= '06'
    UNIT_TRAYS= '07'
    UNIT_BARRELS= '08'
    UNIT_JERRICANS= '09'
    UNIT_BAGS= '10'
    UNIT_CARBOYS= '11'
    UNIT_BOTTLES= '12'
    UNIT_CANISTERS= '13'
    UNIT_TETRABRIKS= '14'
    UNIT_CENTILITERS= '15'
    UNIT_CENTIMITERS= '16'
    UNIT_BINS= '17'
    UNIT_DOZENS= '18'
    UNIT_CASES= '19'
    UNIT_DEMIJOHNS= '20'
    UNIT_GRAMS= '21'
    UNIT_KILOMETERS= '22'
    UNIT_CANS= '23'
    UNIT_BUNCHES= '24'
    UNIT_METERS= '25'
    UNIT_MILIMETERS= '26'
    UNIT_6PACKS= '27'
    UNIT_PACKAGES= '28'
    UNIT_PORTIONS= '29'
    UNIT_ROLLS= '30'
    UNIT_ENVELOPES= '31'
    UNIT_TUBS= '32'
    UNIT_CUBICMETERS= '33'
    UNIT_SECONDS= '34'
    UNIT_WATTS= '35'
    UNIT_KWH= '36'

    SCHEMA_NS= {SCHEMA_3_2:'http://www.facturae.es/Facturae/2009/v3.2/Facturae', SCHEMA_3_2_1:'http://www.facturae.es/Facturae/2014/v3.2.1/Facturae',SCHEMA_3_2_2:'http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml'}
    
    DECIMALS= {'null':{'null':{'min':2, 'max':2},
                       'Item/Quantity':{'min':2, 'max':8},
                       'Item/UnitPriceWithoutTax':{'min':2, 'max':8},
                       'Item/GrossAmount':{'min':2, 'max':8},
                       'Tax/Rate':{'min':2, 'max':8},
                       'Discount/Rate':{'min':2, 'max':8},
                       'Discount/Amount':{'min':2, 'max':2}},
               SCHEMA_3_2:{'null':{'min':2, 'max':2},
                                'Item/Quantity':{'min':2, 'max':6},
                                'Item/TotalAmountWithoutTax':{'min':6, 'max':6},
                                'Item/UnitPriceWithoutTax':{'min':6, 'max':6},
                                'Item/GrossAmount':{'min':6, 'max':6},
                                'Discount/Rate':{'min':4, 'max':4},
                                'Discount/Amount':{'min':6, 'max':6}}
    }
