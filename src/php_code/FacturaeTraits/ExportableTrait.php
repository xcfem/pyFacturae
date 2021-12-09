<?php
namespace josemmo\Facturae\FacturaeTraits;

use josemmo\Facturae\Common\XmlTools;

/**
 * Allows a Facturae instance to be exported to XML.
 */
trait ExportableTrait {

  /**
   * Add optional fields
   * @param  object   $item   Subject item
   * @param  string[] $fields Optional fields
   * @return string           Output XML
   */
  private function addOptionalFields($item, $fields) {
    $tools = new XmlTools();

    $res = "";
    foreach ($fields as $key=>$name) {
      if (is_int($key)) $key = $name; // Allow $item to have a different property name
      if (!empty($item[$key])) {
        $xmlTag = ucfirst($name);
        $res .= "<$xmlTag>" . $tools->escape($item[$key]) . "</$xmlTag>";
      }
    }
    return $res;
  }


  /**
   * Export
   * Get Facturae XML data
   * @param  string     $filePath Path to save invoice
   * @return string|int           XML data|Written file bytes
   */
  public function export($filePath=null) {
    $tools = new XmlTools();

    // Notify extensions
    foreach ($this->extensions as $ext) $ext->__onBeforeExport();

    // Prepare document
    $xml = '<fe:Facturae xmlns:ds="http://www.w3.org/2000/09/xmldsig#" ' .
           'xmlns:fe="' . self::$SCHEMA_NS[$this->version] . '">';
    $totals = $this->getTotals();
    $paymentDetailsXML = $this->getPaymentDetailsXML($totals);

    // Add header
    $batchIdentifier = $this->parties['seller']->taxNumber . $this->header['number'] . $this->header['serie'];
    $xml .= '<FileHeader>' .
              '<SchemaVersion>' . $this->version .'</SchemaVersion>' .
              '<Modality>I</Modality>' .
              '<InvoiceIssuerType>EM</InvoiceIssuerType>' .
              '<Batch>' .
                '<BatchIdentifier>' . $batchIdentifier . '</BatchIdentifier>' .
                '<InvoicesCount>1</InvoicesCount>' .
                '<TotalInvoicesAmount>' .
                  '<TotalAmount>' . $totals['invoiceAmount'] . '</TotalAmount>' .
                '</TotalInvoicesAmount>' .
                '<TotalOutstandingAmount>' .
                  '<TotalAmount>' . $totals['invoiceAmount'] . '</TotalAmount>' .
                '</TotalOutstandingAmount>' .
                '<TotalExecutableAmount>' .
                  '<TotalAmount>' . $totals['invoiceAmount'] . '</TotalAmount>' .
                '</TotalExecutableAmount>' .
                '<InvoiceCurrencyCode>' . $this->currency . '</InvoiceCurrencyCode>' .
              '</Batch>';

    // Add factoring assignment data
    if (!is_null($this->parties['assignee'])) {
      $xml .= '<FactoringAssignmentData>';
      $xml .= '<Assignee>' . $this->parties['assignee']->getXML($this->version) . '</Assignee>';
      $xml .= $paymentDetailsXML;
      if (!is_null($this->header['assignmentClauses'])) {
        $xml .= '<FactoringAssignmentClauses>' .
                  $tools->escape($this->header['assignmentClauses']) .
                '</FactoringAssignmentClauses>';
      }
      $xml .= '</FactoringAssignmentData>';
    }

    // Close header
    $xml .= '</FileHeader>';

    // Add parties
    $xml .= '<Parties>' .
              '<SellerParty>' . $this->parties['seller']->getXML($this->version) . '</SellerParty>' .
              '<BuyerParty>' . $this->parties['buyer']->getXML($this->version) . '</BuyerParty>' .
            '</Parties>';

    // Add invoice data
    $xml .= '<Invoices><Invoice>';
    $xml .= '<InvoiceHeader>' .
        '<InvoiceNumber>' . $this->header['number'] . '</InvoiceNumber>' .
        '<InvoiceSeriesCode>' . $this->header['serie'] . '</InvoiceSeriesCode>' .
        '<InvoiceDocumentType>FC</InvoiceDocumentType>' .
        '<InvoiceClass>OO</InvoiceClass>' .
      '</InvoiceHeader>';
    $xml .= '<InvoiceIssueData>';
    $xml .= '<IssueDate>' . date('Y-m-d', $this->header['issueDate']) . '</IssueDate>';
    if (!is_null($this->header['startDate'])) {
      $xml .= '<InvoicingPeriod>' .
          '<StartDate>' . date('Y-m-d', $this->header['startDate']) . '</StartDate>' .
          '<EndDate>' . date('Y-m-d', $this->header['endDate']) . '</EndDate>' .
        '</InvoicingPeriod>';
    }
    $xml .= '<InvoiceCurrencyCode>' . $this->currency . '</InvoiceCurrencyCode>';
    $xml .= '<TaxCurrencyCode>' . $this->currency . '</TaxCurrencyCode>';
    $xml .= '<LanguageName>' . $this->language . '</LanguageName>';
    $xml .= $this->addOptionalFields($this->header, [
      "description" => "InvoiceDescription",
      "receiverTransactionReference",
      "fileReference",
      "receiverContractReference"
    ]);
    $xml .= '</InvoiceIssueData>';

    // Add invoice taxes
    foreach (["taxesOutputs", "taxesWithheld"] as $taxesGroup) {
      if (count($totals[$taxesGroup]) == 0) continue;
      $xmlTag = ucfirst($taxesGroup); // Just capitalize variable name
      $xml .= "<$xmlTag>";
      foreach ($totals[$taxesGroup] as $type=>$taxRows) {
        foreach ($taxRows as $tax) {
          $xml .= '<Tax>' .
                    '<TaxTypeCode>' . $type . '</TaxTypeCode>' .
                    '<TaxRate>' . $this->pad($tax['rate'], 'Tax/Rate') . '</TaxRate>' .
                    '<TaxableBase>' .
                      '<TotalAmount>' . $this->pad($tax['base'], 'Tax/Base') . '</TotalAmount>' .
                    '</TaxableBase>' .
                    '<TaxAmount>' .
                      '<TotalAmount>' . $this->pad($tax['amount'], 'Tax/Amount') . '</TotalAmount>' .
                    '</TaxAmount>';
          if ($tax['surcharge'] != 0) {
            $xml .= '<EquivalenceSurcharge>' . $this->pad($tax['surcharge'], 'Tax/Surcharge') . '</EquivalenceSurcharge>' .
                    '<EquivalenceSurchargeAmount>' .
                      '<TotalAmount>' . $this->pad($tax['surchargeAmount'], 'Tax/SurchargeAmount') . '</TotalAmount>' .
                    '</EquivalenceSurchargeAmount>';
          }
          $xml .= '</Tax>';
        }
      }
      $xml .= "</$xmlTag>";
    }

    // Add invoice totals
    $xml .= '<InvoiceTotals>';
    $xml .= '<TotalGrossAmount>' . $totals['grossAmount'] . '</TotalGrossAmount>';

    // Add general discounts and charges
    $generalGroups = array(
      ['GeneralDiscounts', 'Discount'],
      ['GeneralSurcharges', 'Charge']
    );
    foreach (['generalDiscounts', 'generalCharges'] as $g=>$groupTag) {
      if (empty($totals[$groupTag])) continue;
      $xmlTag = $generalGroups[$g][1];
      $xml .= '<' . $generalGroups[$g][0] . '>';
      foreach ($totals[$groupTag] as $elem) {
        $xml .= "<$xmlTag>";
        $xml .= "<${xmlTag}Reason>" . $tools->escape($elem['reason']) . "</${xmlTag}Reason>";
        if (!is_null($elem['rate'])) {
          $xml .= "<${xmlTag}Rate>" . $elem['rate'] . "</${xmlTag}Rate>";
        }
        $xml .="<${xmlTag}Amount>" . $elem['amount'] . "</${xmlTag}Amount>";
        $xml .= "</$xmlTag>";
      }
      $xml .= '</' . $generalGroups[$g][0] . '>';
    }

    $xml .= '<TotalGeneralDiscounts>' . $totals['totalGeneralDiscounts'] . '</TotalGeneralDiscounts>';
    $xml .= '<TotalGeneralSurcharges>' . $totals['totalGeneralCharges'] . '</TotalGeneralSurcharges>';
    $xml .= '<TotalGrossAmountBeforeTaxes>' . $totals['grossAmountBeforeTaxes'] . '</TotalGrossAmountBeforeTaxes>';
    $xml .= '<TotalTaxOutputs>' . $totals['totalTaxesOutputs'] . '</TotalTaxOutputs>';
    $xml .= '<TotalTaxesWithheld>' . $totals['totalTaxesWithheld'] . '</TotalTaxesWithheld>';
    $xml .= '<InvoiceTotal>' . $totals['invoiceAmount'] . '</InvoiceTotal>';
    $xml .= '<TotalOutstandingAmount>' . $totals['invoiceAmount'] . '</TotalOutstandingAmount>';
    $xml .= '<TotalExecutableAmount>' . $totals['invoiceAmount'] . '</TotalExecutableAmount>';
    $xml .= '</InvoiceTotals>';

    // Add invoice items
    $xml .= '<Items>';
    foreach ($this->items as $itemObj) {
      $item = $itemObj->getData($this);
      $xml .= '<InvoiceLine>';

      // Add optional fields
      $xml .= $this->addOptionalFields($item, [
        "issuerContractReference", "issuerContractDate",
        "issuerTransactionReference", "issuerTransactionDate",
        "receiverContractReference", "receiverContractDate",
        "receiverTransactionReference", "receiverTransactionDate",
        "fileReference", "fileDate", "sequenceNumber"
      ]);

      // Add required fields
      $xml .= '<ItemDescription>' . $tools->escape($item['name']) . '</ItemDescription>' .
        '<Quantity>' . $item['quantity'] . '</Quantity>' .
        '<UnitOfMeasure>' . $item['unitOfMeasure'] . '</UnitOfMeasure>' .
        '<UnitPriceWithoutTax>' . $item['unitPriceWithoutTax'] . '</UnitPriceWithoutTax>' .
        '<TotalCost>' . $item['totalAmountWithoutTax'] . '</TotalCost>';

      // Add discounts and charges
      $itemGroups = array(
        ['DiscountsAndRebates', 'Discount'],
        ['Charges', 'Charge']
      );
      foreach (['discounts', 'charges'] as $g=>$group) {
        if (empty($item[$group])) continue;
        $groupTag = $itemGroups[$g][1];
        $xml .= '<' . $itemGroups[$g][0] . '>';
        foreach ($item[$group] as $elem) {
          $xml .= "<$groupTag>";
          $xml .= "<${groupTag}Reason>" . $tools->escape($elem['reason']) . "</${groupTag}Reason>";
          if (!is_null($elem['rate'])) {
            $xml .= "<${groupTag}Rate>" . $elem['rate'] . "</${groupTag}Rate>";
          }
          $xml .="<${groupTag}Amount>" . $elem['amount'] . "</${groupTag}Amount>";
          $xml .= "</$groupTag>";
        }
        $xml .= '</' . $itemGroups[$g][0] . '>';
      }

      // Add gross amount
      $xml .= '<GrossAmount>' . $item['grossAmount'] . '</GrossAmount>';

      // Add item taxes
      // NOTE: As you can see here, taxesWithheld is before taxesOutputs.
      // This is intentional, as most official administrations would mark the
      // invoice as invalid XML if the order is incorrect.
      foreach (["taxesWithheld", "taxesOutputs"] as $taxesGroup) {
        if (count($item[$taxesGroup]) == 0) continue;
        $xmlTag = ucfirst($taxesGroup); // Just capitalize variable name
        $xml .= "<$xmlTag>";
        foreach ($item[$taxesGroup] as $type=>$tax) {
          $xml .= '<Tax>' .
                    '<TaxTypeCode>' . $type . '</TaxTypeCode>' .
                    '<TaxRate>' . $this->pad($tax['rate'], 'Tax/Rate') . '</TaxRate>' .
                    '<TaxableBase>' .
                      '<TotalAmount>' . $this->pad($tax['base'], 'Tax/Base') . '</TotalAmount>' .
                    '</TaxableBase>' .
                    '<TaxAmount>' .
                      '<TotalAmount>' . $this->pad($tax['amount'], 'Tax/Amount') . '</TotalAmount>' .
                    '</TaxAmount>';
          if ($tax['surcharge'] != 0) {
            $xml .= '<EquivalenceSurcharge>' . $this->pad($tax['surcharge'], 'Tax/Surcharge') . '</EquivalenceSurcharge>' .
                    '<EquivalenceSurchargeAmount>' .
                      '<TotalAmount>' . $this->pad($tax['surchargeAmount'], 'Tax/SurchargeAmount') . '</TotalAmount>' .
                    '</EquivalenceSurchargeAmount>';
          }
          $xml .= '</Tax>';
        }
        $xml .= "</$xmlTag>";
      }

      // Add more optional fields
      $xml .= $this->addOptionalFields($item, [
        "description" => "AdditionalLineItemInformation",
        "articleCode"
      ]);

      // Close invoice line
      $xml .= '</InvoiceLine>';
    }
    $xml .= '</Items>';

    // Add payment details
    $xml .= $paymentDetailsXML;

    // Add legal literals
    if (count($this->legalLiterals) > 0) {
      $xml .= '<LegalLiterals>';
      foreach ($this->legalLiterals as $reference) {
        $xml .= '<LegalReference>' . $tools->escape($reference) . '</LegalReference>';
      }
      $xml .= '</LegalLiterals>';
    }

    // Add additional data
    $xml .= $this->getAdditionalDataXML();

    // Close invoice and document
    $xml .= '</Invoice></Invoices></fe:Facturae>';
    foreach ($this->extensions as $ext) $xml = $ext->__onBeforeSign($xml);

    // Add signature
    $xml = $this->injectSignature($xml);
    foreach ($this->extensions as $ext) $xml = $ext->__onAfterSign($xml);

    // Prepend content type
    $xml = '<?xml version="1.0" encoding="UTF-8"?>' . "\n" . $xml;

    // Save document
    if (!is_null($filePath)) return file_put_contents($filePath, $xml);
    return $xml;
  }


  /**
   * Get payment details XML
   * @param  array  $totals Invoice totals
   * @return string         Payment details XML, empty string if not available
   */
  private function getPaymentDetailsXML($totals) {
    if (is_null($this->header['paymentMethod'])) return "";

    $dueDate = is_null($this->header['dueDate']) ? $this->header['issueDate'] : $this->header['dueDate'];
    $xml  = '<PaymentDetails>';
    $xml .= '<Installment>';
    $xml .= '<InstallmentDueDate>' . date('Y-m-d', $dueDate) . '</InstallmentDueDate>';
    $xml .= '<InstallmentAmount>' . $totals['invoiceAmount'] . '</InstallmentAmount>';
    $xml .= '<PaymentMeans>' . $this->header['paymentMethod'] . '</PaymentMeans>';
    if (!is_null($this->header['paymentIBAN'])) {
      $accountType = ($this->header['paymentMethod'] == self::PAYMENT_DEBIT) ? "AccountToBeDebited" : "AccountToBeCredited";
      $xml .= "<$accountType>";
      $xml .= '<IBAN>' . $this->header['paymentIBAN'] . '</IBAN>';
      if (!is_null($this->header['paymentBIC'])) {
        $xml .= '<BIC>' . $this->header['paymentBIC'] . '</BIC>';
      }
      $xml .= "</$accountType>";
    }
    $xml .= '</Installment>';
    $xml .= '</PaymentDetails>';

    return $xml;
  }


  /**
   * Get additional data XML
   * @return string Additional data XML
   */
  private function getAdditionalDataXML() {
    $extensionsXML = array();
    foreach ($this->extensions as $ext) {
      $extXML = $ext->__getAdditionalData();
      if (!empty($extXML)) $extensionsXML[] = $extXML;
    }
    $relInvoice =& $this->header['relatedInvoice'];
    $additionalInfo =& $this->header['additionalInformation'];

    // Validate additional data fields
    $hasData = !empty($extensionsXML) || !empty($this->attachments) || !empty($relInvoice) || !empty($additionalInfo);
    if (!$hasData) return "";

    // Generate initial XML block
    $tools = new XmlTools();
    $xml = '<AdditionalData>';
    if (!empty($relInvoice)) $xml .= '<RelatedInvoice>' . $tools->escape($relInvoice) . '</RelatedInvoice>';

    // Add attachments
    if (!empty($this->attachments)) {
      $xml .= '<RelatedDocuments>';
      foreach ($this->attachments as $att) {
        $type = explode('/', $att['file']->getMimeType());
        $type = end($type);
        $xml .= '<Attachment>';
        $xml .= '<AttachmentCompressionAlgorithm>NONE</AttachmentCompressionAlgorithm>';
        $xml .= '<AttachmentFormat>' . $tools->escape($type) . '</AttachmentFormat>';
        $xml .= '<AttachmentEncoding>BASE64</AttachmentEncoding>';
        $xml .= '<AttachmentDescription>' . $tools->escape($att['description']) . '</AttachmentDescription>';
        $xml .= '<AttachmentData>' . base64_encode($att['file']->getData()) . '</AttachmentData>';
        $xml .= '</Attachment>';
      }
      $xml .= '</RelatedDocuments>';
    }

    // Add additional information
    if (!empty($additionalInfo)) {
      $xml .= '<InvoiceAdditionalInformation>' . $tools->escape($additionalInfo) . '</InvoiceAdditionalInformation>';
    }

    // Add extensions data
    if (!empty($extensionsXML)) $xml .= '<Extensions>' . implode('', $extensionsXML) . '</Extensions>';

    $xml .= '</AdditionalData>';
    return $xml;
  }

}
