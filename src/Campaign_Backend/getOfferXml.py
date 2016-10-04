#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from models import OfferData, MemberData


def get_xml(offer_obj):
    xml_string = """<?xml version="1.0" encoding="UTF-8"?>
                    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:off="http://rewards.sears.com/schemas/offer/" xmlns:sch="http://rewards.sears.com/schemas/">
                       <soap:Header />
                       <soap:Body>
                          <off:CreateUpdateOffer>
                             <sch:MessageVersion>01</sch:MessageVersion>
                             <sch:RequestorID>OFRP</sch:RequestorID>
                             <sch:Source>TI</sch:Source>
                             <off:OfferNumber>%s</off:OfferNumber>
                             <off:OfferPointsDollarName>%s</off:OfferPointsDollarName>
                             <off:OfferDescription>%s</off:OfferDescription>
                             <off:OfferType>%s</off:OfferType>
                             <off:OfferSubType>%s</off:OfferSubType>
                             <off:OfferStartDate>%s</off:OfferStartDate>
                             <off:OfferStartTime>%s</off:OfferStartTime>
                             <off:OfferEndDate>%s</off:OfferEndDate>
                             <off:OfferEndTime>%s</off:OfferEndTime>
                             <off:OfferBUProgram>
                                <off:BUProgram>
                                   <off:BUProgramName>%s</off:BUProgramName>
                                   <off:BUProgramCost>%s</off:BUProgramCost>
                                </off:BUProgram>
                             </off:OfferBUProgram>
                             <off:ReceiptDescription>%s</off:ReceiptDescription>
                             <off:OfferCategory>%s</off:OfferCategory>
                             <off:ExpenseAllocation>No allocation ñ Charge all to WH</off:ExpenseAllocation>
                             <off:ModifiedBy>nand</off:ModifiedBy>
                             <off:ModifiedTS>2014-06-25 10:40:00</off:ModifiedTS>
                             <off:OfferAttributes>
                             <off:OfferAttribute>
                                <off:Name>%s</off:Name>
                                <off:Values>
                                   <off:Value>%s</off:Value>
                                </off:Values>
                             </off:OfferAttribute>
                          </off:OfferAttributes>
                          <off:Rules>
                             <off:Rule Entity=\"%s\">
                                <off:Conditions>
                                   <off:Condition>
                                      <off:Name>%s</off:Name>
                                      <off:Operator>%s</off:Operator>
                                      <off:Values>
                                         <off:Value>%s</off:Value>
                                      </off:Values>
                                   </off:Condition>
                                </off:Conditions>
                             </off:Rule>
                             <off:RuleActions>
                                 <off:ActionID>%s</off:ActionID>
                             </off:RuleActions>
                         </off:Rules>
                         <off:Actions>
                            <off:Action ActionID=\"%s\" ActionName=\"%s\">
                               <off:ActionProperties>
                                  <off:ActionProperty PropertyType=\"%s\">
                                     <off:Property>
                                        <off:Name>%s</off:Name>
                                        <off:Values>
                                           <off:Value>%s</off:Value>
                                        </off:Values>
                                     </off:Property>

                                  </off:ActionProperty>
                               </off:ActionProperties>
                            </off:Action>
                         </off:Actions>
                         <off:RealTimeFlag>N</off:RealTimeFlag>
                      </off:CreateUpdateOffer>
                   </soap:Body>
                </soap:Envelope>""" % (offer_obj.OfferNumber,
                                       offer_obj.OfferPointsDollarName,
                                       offer_obj.OfferDescription,
                                       offer_obj.OfferType,
                                       offer_obj.OfferSubType,
                                       offer_obj.OfferStartDate,
                                       offer_obj.OfferStartTime,
                                       offer_obj.OfferEndDate,
                                       offer_obj.OfferEndTime,
                                       offer_obj.OfferBUProgram_BUProgram_BUProgramName,
                                       offer_obj.OfferBUProgram_BUProgram_BUProgramCost,
                                       offer_obj.ReceiptDescription,
                                       offer_obj.OfferCategory,
                                       offer_obj.OfferAttributes_OfferAttribute_Name,
                                       offer_obj.OfferAttributes_OfferAttribute_Values_Value,
                                       offer_obj.Rules_Rule_Entity,
                                       offer_obj.Rules_Conditions_Condition_Name,
                                       offer_obj.Rules_Conditions_Condition_Operator,
                                       offer_obj.Rules_Conditions_Condition_Values_Value,
                                       offer_obj.RuleActions_ActionID,
                                       offer_obj.Actions_ActionID,
                                       offer_obj.Actions_ActionName,
                                       offer_obj.Actions_ActionProperty_PropertyType,
                                       offer_obj.Actions_ActionProperty_Property_Name,
                                       offer_obj.Actions_ActionProperty_Property_Values_Value
                                       )
    return xml_string
