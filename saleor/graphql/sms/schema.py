import graphene

from saleor.graphql.sms.mutations import SendSMS


class SMSMutations(graphene.ObjectType):
    send_sms = SendSMS.Field()
