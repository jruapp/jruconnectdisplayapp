from django.db import models

class ProductEngagementSummary(models.Model):
    product_id = models.IntegerField(primary_key=True)
    stock = models.IntegerField()
    user_id = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    date_posted = models.DateTimeField()
    purchase_count = models.IntegerField()
    likes_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'product_engagement_summary'
        
        


class ViewEngagementsByType(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    engagement_count = models.IntegerField()
    type = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'view_engagements_by_type'


class ViewFeedbackByRating(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    rating_count = models.IntegerField()
    rating = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'view_feedback_by_rating'


class ViewProductEngagementOverTime(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    engagement_count = models.IntegerField()
    product_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'view_product_engagement_over_time'


class ViewSupportInquiriesByStatus(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    status_count = models.IntegerField()
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'view_support_inquiries_by_status'


class UserLikes(models.Model):
    like_id = models.AutoField(primary_key=True)  # Use AutoField for auto-incrementing primary key
    user_id = models.IntegerField()
    liker_id = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically set the field to now when the object is created

    class Meta:
        db_table = 'user_likes'
        managed = False  # Set to True if you want Django to manage this table


class User(models.Model):
    USER_ROLES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    user_id = models.AutoField(primary_key=True)
    stud_id = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=455)
    middle_name = models.CharField(max_length=455)
    last_name = models.CharField(max_length=455)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    profile_url = models.URLField(max_length=255, null=True, blank=True)
    enrollment_url = models.URLField(max_length=455, null=True, blank=True)
    course = models.URLField(max_length=455, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.username})'

    class Meta:
        managed = False
        db_table = 'users'



class TopProductsAll(models.Model):
    product_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    views = models.IntegerField()
    likes = models.IntegerField()
    ratings = models.FloatField()

    class Meta:
        managed = False  # This tells Django not to manage this table (since it's a MySQL view)
        db_table = 'top_10_products_all'  # Make sure this matches the name of your MySQL view



class AllProductsRatings(models.Model):
    row_num = models.IntegerField()
    product_id = models.IntegerField()
    avg_rating = models.FloatField()

    class Meta:
        managed = False  # Prevents Django from trying to create or alter this table
        db_table = "all_products_ratings"  # Matches the database view name



class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    stock = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    ads_url = models.URLField(max_length=255, null=True, blank=True)
    restriction_reason = models.URLField(max_length=255, null=True, blank=True)
    ads_status = models.CharField(max_length=255, default="on_review", blank=True)
    is_sold = models.IntegerField(max_length=11, default="0", blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.user.username}'

    class Meta:
        managed = False
        db_table = 'products'

class Engagement(models.Model):
    ENGAGEMENT_TYPES = [
        ('like', 'Like'),
        ('click', 'Click'),
    ]

    engagement_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=ENGAGEMENT_TYPES)
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        managed = False
        db_table = 'engagement'

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback by {self.user.username} on {self.product.title} - Rating: {self.rating}'

    class Meta:
        managed = False
        db_table = 'feedback'


class AvailedProductDetailsView(models.Model):
    product_id = models.IntegerField()
    product_owner_id = models.IntegerField(null=True)
    title = models.CharField(max_length=455)
    description = models.TextField()
    category = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stock = models.IntegerField(null=True)
    location = models.CharField(max_length=255, null=True)
    image_url = models.CharField(max_length=255, null=True)
    ads_url = models.CharField(max_length=455)
    is_sold = models.IntegerField(default=0)
    date_posted = models.DateTimeField()
    ads_status = models.CharField(max_length=20)
    restriction_reason = models.CharField(max_length=455, null=True)

    avail_id = models.IntegerField(null=True)
    availed_user_id = models.IntegerField(null=True)
    avail_status = models.CharField(max_length=20, null=True)

    first_name = models.CharField(max_length=100, null=True)
    middle_name = models.CharField(max_length=455, null=True)
    last_name = models.CharField(max_length=455, null=True)

    class Meta:
        managed = False
        db_table = 'view_availed_product_details'

class AvailedProduct(models.Model):
    avail_id = models.IntegerField(primary_key=True)
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, db_column='product_id')
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING, db_column='user_id')
    
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)

    class Meta:
        managed = False
        db_table = 'availed_products'


class TopRatedProduct(models.Model):
    product_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=455)
    description = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    ads_url = models.CharField(max_length=455)
    is_sold = models.IntegerField(default=0)
    date_posted = models.DateTimeField(null=True, blank=True)
    ads_status = models.CharField(
        max_length=20,
        choices=[
            ('on_review', 'On Review'),
            ('restricted', 'Restricted'),
            ('deleted', 'Deleted'),
            ('approved', 'Approved')
        ],
        default='on_review'
    )
    restriction_reason = models.CharField(max_length=455, null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    row_num = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = False  # Because this is a view, not a real table
        db_table = 'top_20_rated_products'


class UserMessagesView(models.Model):
    user_id = models.IntegerField(primary_key=True)
    stud_id = models.CharField(max_length=11, blank=True, default='')
    username = models.CharField(max_length=50, null=True)
    password_hash = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=455, null=True, blank=True)
    last_name = models.CharField(max_length=455)
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('admin', 'Admin')], default='student')
    course = models.CharField(max_length=455, null=True, blank=True)
    verified = models.BooleanField(default=False)
    profile_url = models.CharField(max_length=255)
    enrollment_url = models.CharField(max_length=455, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    new_message = models.IntegerField(default=0)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()

    class Meta:
        managed = False  # Prevents Django from trying to create or modify the view
        db_table = "user_messages_view"

    def __str__(self):
        return f"{self.username} ({self.user_id}) - New Messages: {self.new_message}"

class UserProductFeedbackView(models.Model):
    user_id = models.IntegerField()
    stud_id = models.IntegerField()
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=7, choices=[('student', 'Student'), ('admin', 'Admin')])
    verified = models.BooleanField(default=False)
    profile_url = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)
    user_date_created = models.DateTimeField()
    
    product_id = models.IntegerField()
    title = models.CharField(max_length=455)
    description = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField()
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    date_posted = models.DateTimeField()

    feedback_id = models.IntegerField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    feedback_date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_product_feedback_view'

    def __str__(self):
        return f'User {self.username} - Product: {self.title} - Rating: {self.rating}'



class Top5ProductLikes(models.Model):
    product_id = models.IntegerField()
    title = models.CharField(max_length=455)
    image_url = models.CharField(max_length=255)
    likes_count = models.IntegerField()

    class Meta:
        managed = False  # No migration will be created
        db_table = 'top_5_products_likes'


class Top5ProductViews(models.Model):
    product_id = models.IntegerField()
    title = models.CharField(max_length=455)
    image_url = models.CharField(max_length=255)
    views_count = models.IntegerField()

    class Meta:
        managed = False  # No migration will be created
        db_table = 'top_5_products_views'


class Top5ProductRatings(models.Model):
    product_id = models.IntegerField()
    title = models.CharField(max_length=455)
    image_url = models.CharField(max_length=255)
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1)

    class Meta:
        managed = False  # No migration will be created
        db_table = 'top_5_products_ratings'


class Top5CombinedProducts(models.Model):
    product_id = models.IntegerField()
    title = models.CharField(max_length=455)
    image_url = models.CharField(max_length=255)
    combined_score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False  # No migration will be created
        db_table = 'top_5_combined_products'

# Revision
class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_sent = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('read', 'Read'), ('delivered', 'Delivered')], default='delivered')


    def __str__(self):
        return f'Message from {self.sender.username} to {self.receiver.username}'

    class Meta:
        managed = False
        db_table = 'messages'

class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.URLField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    class Meta:
        managed = False
        db_table = 'profiles'

class SupportInquiry(models.Model):
    INQUIRY_STATUSES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]

    inquiry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=INQUIRY_STATUSES, default='open')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Inquiry by {self.user.username} on {self.subject} - Status: {self.get_status_display()}'

    class Meta:
        managed = False
        db_table = 'support_inquiries'
