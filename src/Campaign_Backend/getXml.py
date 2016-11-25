#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import logging
from datetime import datetime
reload(sys)
sys.setdefaultencoding("utf-8")


def get_create_offer_xml(offer_obj):
    xml_string = ""
    try:
        offer_data_dict = dict()
        logging.info("Surprise points::"+str(offer_obj.surprise_points))
        offer_data_dict['campaign_name'] = offer_obj.OfferNumber.split('_')[0]
        offer_data_dict['surprise_points'] = str(offer_obj.surprise_points)
        offer_data_dict['OfferNumber'] = offer_obj.OfferNumber
        offer_data_dict['OfferPointsDollarName'] = offer_obj.OfferPointsDollarName
        offer_data_dict['OfferDescription'] = offer_obj.OfferDescription
        offer_data_dict['OfferType'] = offer_obj.OfferType
        offer_data_dict['OfferSubType'] = offer_obj.OfferSubType
        offer_data_dict['BUProgram_BUProgramName'] = offer_obj.OfferBUProgram_BUProgram_BUProgramName
        offer_data_dict['ReceiptDescription'] = offer_obj.ReceiptDescription
        offer_data_dict['OfferCategory'] = offer_obj.OfferCategory
        offer_data_dict['OfferStartDate'] = offer_obj.OfferStartDate
        offer_data_dict['OfferStartTime'] = offer_obj.OfferStartTime
        offer_data_dict['OfferEndDate'] = offer_obj.OfferEndDate
        offer_data_dict['OfferEndTime'] = offer_obj.OfferEndTime
        offer_data_dict['OfferAttributes_OfferAttribute_Name'] = offer_obj.OfferAttributes_OfferAttribute_Name
        offer_data_dict['OfferAttribute_Values_Value'] = offer_obj.OfferAttributes_OfferAttribute_Values_Value
        offer_data_dict['Rules_Rule_Entity'] = offer_obj.Rules_Rule_Entity
        offer_data_dict['Rules_Conditions_Condition_Name'] = offer_obj.Rules_Conditions_Condition_Name
        offer_data_dict['Rules_Conditions_Condition_Operator'] = offer_obj.Rules_Conditions_Condition_Operator
        offer_data_dict['Rules_Conditions_Condition_Values_Value'] = offer_obj.Rules_Conditions_Condition_Values_Value
        offer_data_dict['RuleActions_ActionID'] = offer_obj.RuleActions_ActionID
        offer_data_dict['Actions_ActionName'] = offer_obj.Actions_ActionName
        offer_data_dict['Actions_ActionID'] = offer_obj.Actions_ActionID
        offer_data_dict['Actions_ActionProperty_PropertyType'] = offer_obj.Actions_ActionProperty_PropertyType
        offer_data_dict['Actions_ActionProperty_Property_Name'] = offer_obj.Actions_ActionProperty_Property_Name
        offer_data_dict['Actions_ActionProperty_Property_Values_Value'] = offer_obj.Actions_ActionProperty_Property_Values_Value

        xml_string = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
                           <soap:Body>
                              <ns2:CreateUpdateOffer xmlns:ns2="http://rewards.sears.com/schemas/offer/" xmlns="http://rewards.sears.com/schemas/">
                                 <MessageVersion>01</MessageVersion>
                                 <RequestorID>OFRP</RequestorID>
                                 <Source>TI</Source>
                                             <ns2:OfferNumber>"""+offer_data_dict['OfferNumber']+"""</ns2:OfferNumber>
                                              <ns2:OfferPointsDollarName>"""+offer_data_dict['OfferPointsDollarName']+"""</ns2:OfferPointsDollarName>
                                 <ns2:OfferDescription>"""+offer_data_dict['OfferDescription']+"""</ns2:OfferDescription>
                                 <ns2:OfferType>"""+offer_data_dict['OfferType']+"""</ns2:OfferType>
                                 <ns2:OfferSubType>"""+offer_data_dict['OfferSubType']+"""</ns2:OfferSubType>
                                 <ns2:OfferBUProgram>
                                    <ns2:BUProgram>
                                       <ns2:BUProgramName>"""+offer_data_dict['BUProgram_BUProgramName']+"""</ns2:BUProgramName>
                                    </ns2:BUProgram>
                                 </ns2:OfferBUProgram>
                                 <ns2:ReceiptDescription>"""+offer_data_dict['ReceiptDescription']+"""</ns2:ReceiptDescription>
                                 <ns2:OfferConditions>TC_XR</ns2:OfferConditions>
                                 <ns2:OfferExclusions>TC_XR</ns2:OfferExclusions>
                                 <ns2:OfferCategory>"""+offer_data_dict['OfferCategory']+"""</ns2:OfferCategory>
                                 <ns2:OfferStartDate>"""+offer_data_dict['OfferStartDate']+"""</ns2:OfferStartDate>
                                 <ns2:OfferStartTime>"""+offer_data_dict['OfferStartTime']+"""</ns2:OfferStartTime>
                                 <ns2:OfferEndDate>"""+offer_data_dict['OfferEndDate']+"""</ns2:OfferEndDate>
                                 <ns2:OfferEndTime>"""+offer_data_dict['OfferEndTime']+"""</ns2:OfferEndTime>
                                 <ns2:ExpenseAllocation>Allocate by Specified %</ns2:ExpenseAllocation>
                                 <ns2:ModifiedBy>xoffdev1</ns2:ModifiedBy>
                                 <ns2:ModifiedTS>"""+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"""</ns2:ModifiedTS>
                                 <ns2:OfferAttributes>
                                    <ns2:OfferAttribute>
                                       <ns2:Name>"""+offer_data_dict['OfferAttributes_OfferAttribute_Name']+"""</ns2:Name>
                                       <ns2:Values>
                                          <ns2:Value>"""+offer_data_dict['OfferAttribute_Values_Value']+"""</ns2:Value>
                                       </ns2:Values>
                                    </ns2:OfferAttribute>
                                    <ns2:OfferAttribute>
                                       <ns2:Name>OFFER_DAILY_IND</ns2:Name>
                                       <ns2:Values>
                                          <ns2:Value>N</ns2:Value>
                                       </ns2:Values>
                                    </ns2:OfferAttribute>
                                 </ns2:OfferAttributes>

                                 <ns2:Rules>
                                    <!--ns2:Rule Entity="Location">
                                       <ns2:Conditions>
                                          <ns2:Condition>
                                             <ns2:Name>STORE_LOCATION</ns2:Name>
                                             <ns2:Operator>EQUALS</ns2:Operator>
                                             <ns2:Values>
                                                <ns2:Value>Order Location</ns2:Value>
                                             </ns2:Values>
                                          </ns2:Condition>
                                          <ns2:Condition>
                                             <ns2:Name>STORE_NUMBERS</ns2:Name>
                                             <ns2:Operator>CONTAINS</ns2:Operator>
                                             <ns2:Values>
                                                <ns2:Value>KPOS</ns2:Value>
                                             </ns2:Values>
                                             <ns2:ConditionAttributes>
                                                <ns2:ConditionAttribute>
                                                   <ns2:Name>NPOS</ns2:Name>
                                                   <ns2:Operator>IN</ns2:Operator>
                                                   <ns2:Values>
                                                      <ns2:Value>01001</ns2:Value>
                                                      <ns2:Value>01003</ns2:Value>
                                                   </ns2:Values>
                                                </ns2:ConditionAttribute>
                                             </ns2:ConditionAttributes>
                                          </ns2:Condition>
                                       </ns2:Conditions>
                                    </ns2:Rule-->


                                    <ns2:Rule Entity="Member">
                                       <ns2:Conditions>
                                          <ns2:Condition>
                                             <ns2:Name>MEMBER_STATUS</ns2:Name>
                                             <ns2:Operator>IN</ns2:Operator>
                                             <ns2:Values>
                                                <ns2:Value>BONUS</ns2:Value>
                                                <ns2:Value>BASE</ns2:Value>
                                             </ns2:Values>
                                          </ns2:Condition>
                                          <ns2:Condition>
                                             <ns2:Name>MEMBER_GROUPS</ns2:Name>
                                             <ns2:Operator>IN</ns2:Operator>
                                             <ns2:Values>
                                                <ns2:Value>"""+offer_data_dict['OfferNumber']+"""</ns2:Value>
                                             </ns2:Values>
                                          </ns2:Condition>
                                       </ns2:Conditions>
                                    </ns2:Rule>
                                    <ns2:Rule Entity=\""""+offer_data_dict['Rules_Rule_Entity']+"""\">
                                       <ns2:Conditions>
                                          <ns2:Condition>
                                             <ns2:Name>"""+offer_data_dict['Rules_Conditions_Condition_Name']+"""</ns2:Name>
                                             <ns2:Operator>"""+offer_data_dict['Rules_Conditions_Condition_Operator']+"""</ns2:Operator>
                                             <ns2:Values>
                                                <ns2:Value>"""+offer_data_dict['Rules_Conditions_Condition_Values_Value']+"""</ns2:Value>
                                             </ns2:Values>
                                          </ns2:Condition>
                                       </ns2:Conditions>
                                    </ns2:Rule>
                                    <ns2:RuleActions>
                                       <ns2:ActionID>"""+offer_data_dict['RuleActions_ActionID']+"""</ns2:ActionID>
                                    </ns2:RuleActions>
                                 </ns2:Rules>
                                 <ns2:Actions>
                                    <ns2:Action ActionName=\""""+offer_data_dict['Actions_ActionName']+"""\" ActionID=\""""+offer_data_dict['Actions_ActionID']+"""\">
                                       <ns2:ActionProperties>
                                          <ns2:ActionProperty>
                                             <ns2:Property>
                                                <ns2:Name>OFFER_THRESHOLD</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value/>
                                                </ns2:Values>
                                             </ns2:Property>
                                             <ns2:Property>
                                                <ns2:Name>OFFER_FOR</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>Spend</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>
                                             <ns2:Property>
                                                <ns2:Name>OFFER_RANGE</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>Flat</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>
                                          </ns2:ActionProperty>
                                          <ns2:ActionProperty PropertyType=\""""+offer_data_dict['Actions_ActionProperty_PropertyType']+"""\">
                                             <ns2:Property>
                                                <ns2:Name>"""+offer_data_dict['Actions_ActionProperty_Property_Name']+"""</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>"""+offer_data_dict['Actions_ActionProperty_Property_Values_Value']+"""</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>

                                             <ns2:Property>
                                                <ns2:Name>FOR_EVERY</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>0</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>
                                             <ns2:Property>
                                                <ns2:Name>VALUE</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>"""+offer_data_dict['surprise_points']+"""</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>
                                             <ns2:Property>
                                                <ns2:Name>CAP</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>"""+offer_data_dict['surprise_points']+""".00</ns2:Value>
                                                </ns2:Values>
                                                </ns2:Property>
                                          </ns2:ActionProperty>
                                          <!--ns2:ActionProperty PropertyType="Cap">
                                             <ns2:Property>
                                                <ns2:Name>MEMBER_TIMES_CAP</ns2:Name>
                                                <ns2:Values>
                                                   <ns2:Value>1</ns2:Value>
                                                </ns2:Values>
                                             </ns2:Property>
                                          </ns2:ActionProperty-->
                                       </ns2:ActionProperties>
                                    </ns2:Action>
                                 </ns2:Actions>
                                 <ns2:RealTimeFlag>Y</ns2:RealTimeFlag>
                              </ns2:CreateUpdateOffer>
                           </soap:Body>
                        </soap:Envelope>"""
    except:
        e = sys.exc_info()[0]
        logging.info("Oops!  That was no valid number.  Try again... : %s", e)

    return xml_string


def get_update_offer_xml(offer_entity):
    xml_string = """<S:Envelope xmlns:S="http://www.w3.org/2003/05/soap-envelope">
                   <S:Body>
                      <ns2:UpdateOfferStatus xmlns="http://rewards.sears.com/schemas/" xmlns:ns2="http://rewards.sears.com/schemas/offer/">
                         <MessageVersion>01</MessageVersion>
                         <RequestorID>OFRP</RequestorID>
                         <Source>TI</Source>
                         <ns2:ModifiedTS>"""+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"""</ns2:ModifiedTS>
                         <ns2:ModifiedBy>xoff</ns2:ModifiedBy>
                         <ns2:OffersInfo>
                            <ns2:OfferInfo>
                               <ns2:OfferNumber>"""+offer_entity.OfferNumber+"""</ns2:OfferNumber>
                               <ns2:OfferStatus>ACTIVATED</ns2:OfferStatus>
                            </ns2:OfferInfo>
                         </ns2:OffersInfo>
                         <ns2:AdditionalAttributes>
                            <ns2:AdditionalAttribute>
                               <ns2:Name>RealTimeFlag</ns2:Name>
                               <ns2:Values>
                                  <ns2:Value>Y</ns2:Value>
                               </ns2:Values>
                            </ns2:AdditionalAttribute>
                         </ns2:AdditionalAttributes>
                      </ns2:UpdateOfferStatus>
                   </S:Body>
                </S:Envelope>"""
    return xml_string


def get_register_offer_xml(offer_entity, member_entity):
    end_date = offer_entity.OfferEndDate+"T"+offer_entity.OfferEndTime
    xml_string = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:web="http://www.epsilon.com/webservices/">
                   <soap:Header/>
                   <soap:Body>
                      <web:OfferRegistration>
                         <web:MessageVersion>01</web:MessageVersion>
                         <web:ActionTag>A</web:ActionTag>

                         <web:MemberNumber>"""+member_entity.member_id+"""</web:MemberNumber>
                         <web:RequestorID>NPOS</web:RequestorID>
                         <web:AssociateID>000000000000</web:AssociateID>
                         <web:RegisterNumber>001</web:RegisterNumber>
                         <web:StoreNumber>00800</web:StoreNumber>
                         <web:RegistrationStartDTTM>"""+datetime.now().strftime("%Y-%m-%dT%H:%M:%S")+"""</web:RegistrationStartDTTM>
                         <web:RegistrationEndDTTM>"""+end_date+"""</web:RegistrationEndDTTM>
                         <web:MemberOfferReset>N</web:MemberOfferReset>
                         <web:OfferMemberGroupList>
                            <web:OfferMemberGroup>
                               <web:OfferCode>"""+offer_entity.OfferNumber+"""</web:OfferCode><web:GroupName>"""+offer_entity.OfferNumber+"""</web:GroupName>
                            </web:OfferMemberGroup>
                         </web:OfferMemberGroupList>
                      </web:OfferRegistration>
                   </soap:Body>
                </soap:Envelope>"""
    return xml_string


def get_balance_xml():
    curr_date = datetime.now()
    xml_string = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:web="http://www.epsilon.com/webservices/">
                   <soap:Header/>
                   <soap:Body>
                      <web:ProcessRedemption>
                         <web:MessageVersion>06</web:MessageVersion>
                         <web:Function>B</web:Function>
                         <web:RequestorID>NPOS</web:RequestorID>
                         <web:MemberNumber>7081317702051967</web:MemberNumber>
                         <web:PickUpStoreNumber>01168</web:PickUpStoreNumber>
                         <web:OrderStoreNumber>01168</web:OrderStoreNumber>
                         <web:RegisterNumber>057</web:RegisterNumber>
                         <web:TransactionDate>"""+curr_date.strftime("%Y-%m-%d")+"""</web:TransactionDate>
                         <web:TransactionTime>"""+curr_date.strftime("%H:%M:%S")+"""</web:TransactionTime>
                         <web:AssociateID>003574</web:AssociateID>
                         <web:RedemptionPoints>0</web:RedemptionPoints>
                         <web:RedemptionDollarValue>0</web:RedemptionDollarValue>
                         <web:MaxRedeemablePoints>0</web:MaxRedeemablePoints>
                         <web:MaxRedeemableDollarValue>0</web:MaxRedeemableDollarValue>
                         <web:TotalAvailableRewardPoints>0</web:TotalAvailableRewardPoints>
                         <web:LayawayFlag>0</web:LayawayFlag>
                         <web:LineItems>
                            <web:LineItem>
                               <web:LineNumber>1</web:LineNumber>
                               <web:ItemType>1</web:ItemType>
                               <web:Division>76</web:Division>
                               <web:ItemNumber>5332</web:ItemNumber>
                               <web:LineItemAmountTypeCode>1</web:LineItemAmountTypeCode>
                               <web:DollarValuePreDisc>50.00</web:DollarValuePreDisc>
                               <web:DollarValuePostDisc>50.00</web:DollarValuePostDisc>
                               <web:PriceMatchAmount>0</web:PriceMatchAmount>
                               <web:PriceMatchBonusAmount>0</web:PriceMatchBonusAmount>
                               <web:Quantity>1</web:Quantity>
                               <web:PointsRedeemed>0</web:PointsRedeemed>
                               <web:DollarValueOfPointsRedeemed>0</web:DollarValueOfPointsRedeemed>
                               <web:RedemptionExclusionFlag>N</web:RedemptionExclusionFlag>
                               <web:TaxAmount>0.00</web:TaxAmount>
                               <web:PostSalesAdjustmentAmount>0</web:PostSalesAdjustmentAmount>
                               <web:NonMemberPrice>0</web:NonMemberPrice>
                            </web:LineItem>
                         </web:LineItems>
                      </web:ProcessRedemption>
                   </soap:Body>
                </soap:Envelope>"""
    logging.info("XML String:: %s" % xml_string)
    return xml_string


def get_redeem_offer_xml():
    curr_date = datetime.now()
    xml_string = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:web="http://www.epsilon.com/webservices/">
                   <soap:Header/>
                   <soap:Body>
                      <web:ProcessRedemption>
                         <web:MessageVersion>06</web:MessageVersion>
                         <web:Function>R</web:Function>
                         <web:RequestorID>NPOS</web:RequestorID>
                         <web:MemberNumber>7081317702051967</web:MemberNumber>
                         <web:PickUpStoreNumber>01168</web:PickUpStoreNumber>
                         <web:OrderStoreNumber>01168</web:OrderStoreNumber>
                         <web:RegisterNumber>057</web:RegisterNumber>
                         <<web:TransactionDate>"""+curr_date.strftime("%Y-%m-%d")+"""</web:TransactionDate>
                         <web:TransactionTime>"""+curr_date.strftime("%H:%M:%S")+"""</web:TransactionTime>
                         <web:AssociateID>003574</web:AssociateID>
                         <web:RedemptionPoints>2830</web:RedemptionPoints>
                         <web:RedemptionDollarValue>2.83</web:RedemptionDollarValue>
                         <web:MaxRedeemablePoints>2838</web:MaxRedeemablePoints>
                         <web:MaxRedeemableDollarValue>2.83</web:MaxRedeemableDollarValue>
                         <web:TotalAvailableRewardPoints>2838</web:TotalAvailableRewardPoints>
                         <web:LayawayFlag>0</web:LayawayFlag>
                         <web:LineItems>
                            <web:LineItem>
                               <web:LineNumber>1</web:LineNumber>
                               <web:ItemType>1</web:ItemType>
                               <web:Division>76</web:Division>
                               <web:ItemNumber>5332</web:ItemNumber>
                               <web:LineItemAmountTypeCode>1</web:LineItemAmountTypeCode>
                               <web:DollarValuePreDisc>50.00</web:DollarValuePreDisc>
                               <web:DollarValuePostDisc>50.00</web:DollarValuePostDisc>
                               <web:PriceMatchAmount>0</web:PriceMatchAmount>
                               <web:PriceMatchBonusAmount>0</web:PriceMatchBonusAmount>
                               <web:Quantity>1</web:Quantity>
                               <web:PointsRedeemed>0</web:PointsRedeemed>
                               <web:DollarValueOfPointsRedeemed>0</web:DollarValueOfPointsRedeemed>
                               <web:RedemptionExclusionFlag>N</web:RedemptionExclusionFlag>
                               <web:TaxAmount>0.00</web:TaxAmount>
                               <web:PostSalesAdjustmentAmount>0</web:PostSalesAdjustmentAmount>
                               <web:NonMemberPrice>0</web:NonMemberPrice>
                            </web:LineItem>
                         </web:LineItems>
                      </web:ProcessRedemption>
                   </soap:Body>
                </soap:Envelope>"""
    return xml_string

