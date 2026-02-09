from rest_framework_simplejwt.authentication import JWTAuthentication
from bson import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed

class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token['user_id']
        try:
            # Convert string ID to ObjectId for MongoDB lookup
            if isinstance(user_id, str) and len(user_id) == 24:
                try:
                    user_id = ObjectId(user_id)
                except:
                    pass
            
            # Simple lookup using the primary key field (which is _id in our case)
            user = self.user_model.objects.get(**{self.user_model._meta.pk.name: user_id})
            
            if not user.is_active:
                raise AuthenticationFailed('User is inactive', code='user_inactive')
                
            return user
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')
        except Exception as e:
            # Fallback for other errors to help debug
            print(f"Auth lookup error: {str(e)}")
            raise AuthenticationFailed(f'Auth error: {str(e)}', code='auth_error')
