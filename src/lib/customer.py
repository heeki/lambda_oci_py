import json
import uuid

class Customer:
    def __init__(self, ddb, table):
        self.ddb = ddb
        self.table = table
        self.uid = None
        self.given_name = None
        self.family_name = None
        self.birthdate = None
        self.email = None
        self.phone_number = None
        self.phone_number_verified = False

    def __repr__(self):
        return {
            "uid": self.uid,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "birthdate": self.birthdate,
            "email": self.email,
            "phone_number":  self.phone_number,
            "phone_number_verified": self.phone_number_verified
        }

    def __str__(self):
        return json.dumps(self.__repr__())

    def set_uid(self, value):
        self.uid = value
    
    def set_given_name(self, value):
        self.given_name = value
    
    def set_family_name(self, value):
        self.family_name = value

    def set_birthdate(self, value):
        self.birthdate = value

    def set_email(self, value):
        self.email = value

    def set_phone_number(self, value):
        self.phone_number = value

    def set_phone_number_verified(self, value):
        self.phone_number_verified = value

    def get_all(self):
        response = self.ddb.scan(
            TableName = self.table,
            IndexName = "lu_email",
            Limit = 100
        )
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": []
        }
        for item in response["Items"]:
            output["ResponseBody"].append({
                "email": item["email"]["S"],
                "uid": item["uid"]["S"]
            })
        return output

    def get(self, uid):
        response = self.ddb.get_item(
            TableName = self.table,
            Key = {
                "uid": {
                    "S": uid
                }
            }
        )
        self.set_uid(uid)
        self.set_given_name(response["Item"]["given_name"]["S"])
        self.set_family_name(response["Item"]["family_name"]["S"])
        self.set_birthdate(response["Item"]["birthdate"]["S"])
        self.set_email(response["Item"]["email"]["S"])
        self.set_phone_number(response["Item"]["phone_number"]["S"])
        self.set_phone_number_verified(response["Item"]["phone_number_verified"]["BOOL"])
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": self.__repr__()
        }
        return output

    def exists(self, email):
        response = self.ddb.query(
            TableName = self.table,
            IndexName = "lu_email",
            KeyConditionExpression = "email = :val1",
            ExpressionAttributeValues = {
                ":val1": {
                    "S": email
                }
            }
        )
        item_count = len(response["Items"])
        return item_count

    def create(self):
        self.uid = str(uuid.uuid4())
        if (self.exists(self.email) == 0):
            response = self.ddb.put_item(
                TableName = self.table,
                Item = {
                    "uid": { "S": self.uid },
                    "given_name": { "S": self.given_name },
                    "family_name": { "S": self.family_name },
                    "birthdate": { "S": self.birthdate },
                    "email": { "S": self.email },
                    "phone_number": { "S": self.phone_number },
                    "phone_number_verified": { "BOOL": self.phone_number_verified }
                }
            )
            output = {
                "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
                "ResponseBody": self.__repr__()
            }
        else:
            output = {
                "HTTPStatusCode": 500,
                "ResponseBody": {
                    "ErrorMessage": "Email already exists",
                    "ErrorType": "InputError",
                }
            }
        return output

    def generate_ddb_update_expr(self):
        update_expr = ["set "]
        for k in self.__repr__():
            if (k != "uid"):
                update_expr.append(f"{k}=:{k}, ")
        final_expr = "".join(update_expr)
        return final_expr[:-2]

    def generate_ddb_expr_vals(self):
        return {
            ":given_name": { "S": self.given_name },
            ":family_name": { "S": self.family_name },
            ":birthdate": { "S": self.birthdate },
            ":email": { "S": self.email },
            ":phone_number": { "S": self.phone_number },
            ":phone_number_verified": { "BOOL": self.phone_number_verified }
        }

    def update(self, uid):
        self.uid = uid
        update_expr = self.generate_ddb_update_expr()
        update_vals = self.generate_ddb_expr_vals()
        print(json.dumps(update_expr))
        print(json.dumps(update_vals))
        response = self.ddb.update_item(
            TableName = self.table,
            Key = {
                "uid": { "S": self.uid }
            },
            UpdateExpression = update_expr,
            ExpressionAttributeValues = update_vals
        )
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": response["ResponseMetadata"]["RequestId"]
        }
        return output

    def delete(self, uid):
        response = self.ddb.delete_item(
            TableName = self.table,
            Key = {
                "uid": { "S": uid }
            },
            ReturnValues = "ALL_OLD"
        )
        print(json.dumps(response))
        self.set_uid(uid)
        self.set_given_name(response["Attributes"]["given_name"]["S"])
        self.set_family_name(response["Attributes"]["family_name"]["S"])
        self.set_birthdate(response["Attributes"]["birthdate"]["S"])
        self.set_email(response["Attributes"]["email"]["S"])
        self.set_phone_number(response["Attributes"]["phone_number"]["S"])
        self.set_phone_number_verified(response["Attributes"]["phone_number_verified"]["BOOL"])
        output = {
            "HTTPStatusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "ResponseBody": self.__repr__()
        }
        return output