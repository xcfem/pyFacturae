# -*- coding: utf-8 -*-

class XmlTools(object):

  def escape(value):
    '''Escape XML value

       :param  string value Input value
       :return string        Escaped input
    '''
    return htmlspecialchars(value, ENT_XML1, 'UTF-8')


  def randomId():
    '''
       Generate random ID

       This method is used for generating random IDs required when signing the
       document.

       :return int Random number
    '''
    retval= None
    if (function_exists('random_int')):
        retval= random_int(0x10000000, 0x7FFFFFFF)
    else:
        retval= rand(100000, 999999)
    return retval

  def injectNamespaces(xml, newNs):
      '''
         Inject namespaces
         :param  string          xml   Input XML
         :param  string|string[] newNs Namespaces
         :return string                 Canonicalized XML with new namespaces
      '''
      #if (!is_array(newNs)) newNs = array(newNs)
      xml = explode(">", xml, 2)
      oldNs = explode(" ", xml[0])
      elementName = array_shift(oldNs)

      # Combine and sort namespaces
      xmlns = array()
      attributes = array()
      allNs= oldNs+newNs
      for name in allNs:
        if(strpos(name, 'xmlns:') == 0):
          xmlns.append(name)
        else:
          attributes.append(name)
      sort(xmlns)
      sort(attributes)
      ns = array_merge(xmlns, attributes)

      # Generate new XML element
      xml = elementName + " " + implode(' ', ns) + ">" + xml[1]
      return xml


  def toBase64(bytes, pretty= False):
    '''
       To Base64
       :param  string  bytes  Input
       :param  boolean pretty Pretty Base64 response
       :return string          Base64 response
    '''
    res = base64_encode(bytes)
    if(pretty):
        return this.prettify(res)
    else:
        return res

  def prettify(input):
    '''
       Prettify
       :param  input: Input string
       :return Multi-line response
    '''
    return chunk_split(input, 76, "\n")

  def getDigest(input, pretty= False):
    '''
       Get digest in SHA-512
       :param  string  input  Input string
       :param  boolean pretty Pretty Base64 response
       :return string          Digest
    '''
    return this.toBase64(hash("sha512", input, True), pretty)


  def getCert(pem, pretty= True):
    '''
       Get certificate
       :param  string  pem    Certificate for the public key in PEM format
       :param  boolean pretty Pretty Base64 response
       :return string          Base64 Certificate
    '''
    pem = str_replace("-----BEGIN CERTIFICATE-----", "", pem)
    pem = str_replace("-----END CERTIFICATE-----", "", pem)
    pem = str_replace("\n", "", str_replace("\r", "", pem))
    if(pretty):
        pem = this.prettify(pem)
    return pem


  def getCertDigest(publicKey, pretty= False):
    '''
       Get certificate digest in SHA-512
       :param  string  publicKey Public Key
       :param  boolean pretty    Pretty Base64 response
       :return Base64 Digest
    '''
    digest = openssl_x509_fingerprint(publicKey, "sha512", True)
    return this.toBase64(digest, pretty)


  def getSignature(payload, privateKey, pretty= True):
      '''
         Get signature in SHA-1
         :param  string  payload    Data to sign
         :param  string  privateKey Private Key
         :param  boolean pretty     Pretty Base64 response
         :return string              Base64 Signature
      '''
      openssl_sign(payload, signature, privateKey)
      return this.toBase64(signature, pretty)

