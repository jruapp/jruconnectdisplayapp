from datetime import timezone
from django.http import HttpResponse,JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout
from jruconnect import settings
from .models import RandomProductPerCategory, TopRatedProduct, AvailedProductDetailsView, AvailedProduct, UserMessagesView, AllProductsRatings, Product, User, Engagement, Feedback, Message, Profile, SupportInquiry, ProductEngagementSummary, ViewEngagementsByType, ViewProductEngagementOverTime, ViewFeedbackByRating, ViewSupportInquiriesByStatus, UserLikes, UserProductFeedbackView, Top5ProductLikes, Top5ProductViews, Top5ProductRatings, Top5CombinedProducts, TopProductsAll
import json
import os
from django.db.models import Q
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count
import random
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail
from django.http import HttpRequest
import pandas as pd 



def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a 6-digit OTP

def send_otp_email(email):
    otp = generate_otp()
    expires_at = now() + timedelta(minutes=10)  # OTP expires in 10 minutes

    subject = "Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}. It expires in 10 minutes."
    from_email = "qwertylord1222@gmail.com"  # Replace with your Gmail
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def request_otp(request):
    response_data = "-"
    if request.method == 'POST':
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            send_otp_email(email)  # Send OTP to email
            response_data = "OTP has been sent to your email"
            status_code = 200
            request.session['email_forgot_pass'] =  email
            return redirect('change_password')
        else:
            response_data = "Email does not exist in our records."
            status_code = 400


    return render(request, 'views/forgot-password.html', { "response_data": response_data})  # Render Forgot Password page

def verify_otp_and_reset_password(request):
    if request.method == 'POST':
        email = request.session.get('email_forgot_pass', '')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        user = get_object_or_404(User, email=email)

        if user:
            user.password_hash = new_password
            user.save()
            redirect('login')
        else: 
            return render(request, 'views/change-password.html', { "response_data": "non exisitent email!"})

        return render(request, 'views/change-password.html', { "response_data": "Invalid or expired OTP."})

    return render(request, 'views/change-password.html')  # Renders Change Password page

def product_engagement_trends():
    return (
        Engagement.objects
        .values('product_id')
        .annotate(engagement_count=Count('engagement_id'))
        .order_by('-engagement_count')
    )

def create_interaction_matrix():
    engagements = Engagement.objects.all()
    data = {
        'user_id': [engagement.user_id for engagement in engagements],
        'product_id': [engagement.product_id for engagement in engagements],
        'engagement_type': [engagement.type for engagement in engagements],
    }
    df = pd.DataFrame(data)
    interaction_matrix = df.pivot_table(index='user_id', columns='product_id', values='engagement_type', aggfunc='count', fill_value=0)
    return interaction_matrix

def recommend_products(user_id, interaction_matrix):
    model = NearestNeighbors(metric='cosine')
    model.fit(interaction_matrix.values)
    user_index = interaction_matrix.index.get_loc(user_id)
    distances, indices = model.kneighbors(interaction_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=5)
    recommended_products = interaction_matrix.columns[indices.flatten()]
    return recommended_products

def create_product_profiles():
    products = Product.objects.all()
    product_descriptions = [f"{product.title} {product.description}" for product in products]
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(product_descriptions)
    return tfidf_matrix, products

def recommend_similar_products(product_id, tfidf_matrix):
    cosine_sim = cosine_similarity(tfidf_matrix)
    similar_indices = cosine_sim[product_id].argsort()[-6:-1][::-1]  # Top 5 similar products
    return similar_indices

def recommend_for_user(user_id):
    interaction_matrix = create_interaction_matrix()
    recommended_collab = recommend_products(user_id, interaction_matrix)

    # Example: recommend similar products for a specific product_id
    product_id = 1  # Replace with actual logic to get a relevant product_id
    tfidf_matrix, products = create_product_profiles()
    recommended_content = recommend_similar_products(product_id, tfidf_matrix)

    return {
        "collab_recommendations": recommended_collab,
        "content_recommendations": [products[i] for i in recommended_content],
    }

def recommendations_view(request):
    if request.user.is_authenticated:
        user_id = request.user.user_id
        recommendations = recommend_for_user(user_id)
        
        return render(request, 'recommendations.html', {
            'collab_recommendations': recommendations['collab_recommendations'],
            'content_recommendations': recommendations['content_recommendations'],
            'engagement_trends': product_engagement_trends(),
        })
    else:
        return render(request, 'recommendations.html', {
            'message': 'Please log in to see recommendations.'
        })

    combined = list(Top5CombinedProducts.objects.all())
from decimal import Decimal
def convert_decimal_to_float(data):
    for item in data:
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)
    return data

def home(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    if role != 'admin':
        return redirect('advertisements')

    # Fetch data from the database
    view_engagements_by_type = ViewEngagementsByType.objects.all()
    view_feedback_by_rating = ViewFeedbackByRating.objects.all()
    top_products = TopProductsAll.objects.all()
    view_product_engagement_over_time = ViewProductEngagementOverTime.objects.all()
    view_support_inquiries_by_status = ViewSupportInquiriesByStatus.objects.all()
    likes = list(Top5ProductLikes.objects.values("product_id", "title", "image_url", "likes_count"))
    views = list(Top5ProductViews.objects.values("product_id", "title", "image_url", "views_count"))
    ratings = list(Top5ProductRatings.objects.values("product_id", "title", "image_url", "avg_rating"))
    combined = list(Top5CombinedProducts.objects.values("product_id", "title", "image_url", "combined_score"))

    # Convert Decimal fields to float
    ratings = convert_decimal_to_float(ratings)
    combined = convert_decimal_to_float(combined)
    
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found


    # Prepare context
    context = {
        'full_name': full_name,
        'role': role,
        'admin_id': admin_id,
        'admin_user': admin_user,
        'view_engagements_by_type': view_engagements_by_type,
        'view_feedback_by_rating': view_feedback_by_rating,
        'view_product_engagement_over_time': view_product_engagement_over_time,
        'view_support_inquiries_by_status': view_support_inquiries_by_status,

        "likes": json.dumps(likes),
        "views": json.dumps(views),
        "ratings": json.dumps(ratings),
        "combined": json.dumps(combined),
        'top_products' : top_products
    }

    return render(request, 'views/index.html', context)

#'collab_recommendations': recommendations.get('collab_recommendations', []),
#'content_recommendations': recommendations.get('content_recommendations', []),
# Recommendations
#    recommendations = {}
 #   if request.user.is_authenticated:
 #       user_id = admin_id
 #       recommendations = recommend_for_user(user_id)  # Call the recommendation function


from django.http import JsonResponse
from .models import ViewEngagementsByType, ViewFeedbackByRating, ViewProductEngagementOverTime, ViewSupportInquiriesByStatus

def get_engagements_by_type(request):
    data = list(ViewEngagementsByType.objects.values('year', 'month', 'engagement_count', 'type'))
    return JsonResponse(data, safe=False)

def get_feedback_by_rating(request):
    data = list(ViewFeedbackByRating.objects.values('year', 'month', 'rating_count', 'rating'))
    return JsonResponse(data, safe=False)

def get_product_engagement_over_time(request):
    data = list(ViewProductEngagementOverTime.objects.values('year', 'month', 'engagement_count', 'product_id'))
    return JsonResponse(data, safe=False)

def get_support_inquiries_by_status(request):
    data = list(ViewSupportInquiriesByStatus.objects.values('year', 'month', 'status_count', 'status'))
    return JsonResponse(data, safe=False)
@csrf_exempt
def register(request):
    
    if request.method == 'POST':
        try:
            # Handle profile image upload
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                image_folder = os.path.join(settings.BASE_DIR, 'staticfiles', 'profile_images')
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                image_path = os.path.join(image_folder, profile_image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in profile_image.chunks():
                        destination.write(chunk)
                profile_image_url = os.path.join('profile_images', profile_image.name)
            else:
                profile_image_url = None

            # Handle enrollment form PDF upload
            enrollment_form = request.FILES.get('enrollment_form')
            if enrollment_form:
                enrollment_folder = os.path.join(settings.BASE_DIR, 'staticfiles', 'enrollment_forms')
                if not os.path.exists(enrollment_folder):
                    os.makedirs(enrollment_folder)
                enrollment_path = os.path.join(enrollment_folder, enrollment_form.name)
                with open(enrollment_path, 'wb+') as destination:
                    for chunk in enrollment_form.chunks():
                        destination.write(chunk)
                enrollment_form_url = os.path.join('enrollment_forms', enrollment_form.name)
            else:
                enrollment_form_url = None

            # Create user object and save
            user = User(
                stud_id=request.POST.get('user_id'),
                username=request.POST.get('username'),
                first_name=request.POST.get('first_name'),
                middle_name=request.POST.get('middle_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                password_hash=request.POST.get('password'),  # Hash the password appropriately
                course=request.POST.get('role'),
                role="student",
                verified=request.POST.get('verified') == 'on',
                is_new_user="yes",
                profile_url=profile_image_url,
                enrollment_url=enrollment_form_url
            )
            user.save()

            return redirect('login')  # Redirect after successful registration
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    email_user = "na"
    first_name = "na"
    last_name = "na"
    username = "na"
    if request.user.is_authenticated:
        # Only try to access the email if the user is authenticated
        if hasattr(request.user, 'email'):
            email_user = request.user.email
            first_name = request.user.first_name
            last_name = request.user.last_name
            username = request.user.username
           
    
    return render(request, 'views/register.html', {'email_user' :email_user, 'first_name' :first_name, 'last_name' : last_name, 'username': username})

def view(request):
    return render(request, 'views/view.html')



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Query the user by username
        try:
            user = User.objects.get(email=username, verified=1)
        except User.DoesNotExist:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
        
        # Check password (assuming password_hash is a hashed password)
        if user.password_hash == password:  # Ideally, use a password hashing library
            request.session['admin_id'] = user.user_id  # Set session variable
            request.session['full_name'] = f"{user.first_name} {user.middle_name} {user.last_name}"  # Set session variable
            request.session['role'] = user.role  # Set session variable
            return redirect('home')
        else:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
    
    if request.user.is_authenticated:
        # Only try to access the email if the user is authenticated
        if hasattr(request.user, 'email'):
            # Query the user by email
            try:
                user = User.objects.get(email=request.user.email, verified=1)
            except User.DoesNotExist:
                logout(request)  # This will clear the session data and log out the user
                google_logout_url = 'https://accounts.google.com/Logout'
                return render(request, 'views/login.html', {'message_g' : 'You email does not exist in the system, register first' })
            
            # Set session variables
            request.session['admin_id'] = user.user_id
            request.session['full_name'] = f"{user.first_name} {user.middle_name} {user.last_name}"
            request.session['role'] = user.role 
            return redirect('home')
    emailnow = getattr(request.user, 'email', 'None')

    # In case user is not authenticated or email doesn't exist
    return render(request, 'views/login.html', {'email' : emailnow, 'email2' : 'tryemai' })




def loginstud(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Query the user by username
        try:
            user = User.objects.get(email=username, verified=1, role="student")
        except User.DoesNotExist:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
        
        # Check password (assuming password_hash is a hashed password)
        if user.password_hash == password:  # Ideally, use a password hashing library
            request.session['admin_id'] = user.user_id  # Set session variable
            request.session['full_name'] = f"{user.first_name} {user.middle_name} {user.last_name}"  # Set session variable
            request.session['role'] = user.role  # Set session variable
            return redirect('home')
        else:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
    return render(request, 'views/login-stud.html')


def loginadmin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Query the user by username
        try:
            user = User.objects.get(email=username, role="admin", verified=1)
        except User.DoesNotExist:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
        
        # Check password (assuming password_hash is a hashed password)
        if user.password_hash == password:  # Ideally, use a password hashing library
            request.session['admin_id'] = user.user_id  # Set session variable
            request.session['full_name'] = f"{user.first_name} {user.middle_name} {user.last_name}"  # Set session variable
            request.session['role'] = user.role  # Set session variable
            return redirect('home')
        else:
            return render(request, 'views/login.html', {'error': 'Invalid credentials'})
    return render(request, 'views/login.html')

def products(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
   
    all_products = Product.objects.select_related('user')
    context = {'products': all_products, 'full_name': full_name, 'admin_id' : admin_id, 'role': role, 'admin_user': admin_user }
    return render(request, 'views/products.html', context)



def products_student(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
   
    all_products = Product.objects.filter(user_id=admin_id)
    context = {'products': all_products, 'full_name': full_name, 'admin_id' : admin_id, 'role': role, 'admin_user': admin_user }
    return render(request, 'views/products.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, Product, UserLikes

def user_profile(request, user_profile_id):
    # Fetch session values
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id')  # No default '0', treat it as None if absent
    role = request.session.get('role', '')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found

    # Fetch all products related to the admin user
    user_detail = User.objects.filter(user_id=user_profile_id) if user_profile_id else []
    all_products = Product.objects.filter(user_id=user_profile_id) if user_profile_id else []
    like_tbl = UserLikes.objects.all()
    
    # Count likes for the user profile
    count_likes = UserLikes.objects.filter(user_id=user_profile_id).count() if user_profile_id else 0

    if request.method == 'POST':
        liker_id = request.POST.get('liker_id')  # Get the liker ID from the form data

        if liker_id:
            # Create a new like entry
            new_like = UserLikes(user_id=user_profile_id, liker_id=admin_id)  # assuming the logged-in user is the liker
            new_like.save()
            # Optionally, redirect to the same profile page after saving
            return redirect('user_profile', user_profile_id=user_profile_id)

    context = {
        'products': all_products,
        'full_name': full_name,
        'admin_id': admin_id,
        'role': role,
        'admin_user': admin_user,
        'user_detail': user_detail,
        'count_likes': count_likes,
        'like_tbl': like_tbl
    }

    return render(request, 'views/u-profile.html', context)



def view_product(request, product_id):
    # Fetch session values
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id')  # No default '0', treat it as None if absent
    role = request.session.get('role', '')

    current_url = request.build_absolute_uri()

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found

    # Fetch the product by product_id
    try:
        product = Product.objects.get(product_id=product_id)
        category = product.category  # Get the category of the current product
    except Product.DoesNotExist:
        product = None
        category = None

    # Fetch products that belong to the same category
    products = ProductEngagementSummary.objects.filter(category=category) if category else []

    # Fetch product engagement details (e.g., likes)
    engagement_summary = ProductEngagementSummary.objects.filter(product_id=product_id)
    feedback = UserProductFeedbackView.objects.filter(product_id=product_id)
    is_liked = Engagement.objects.filter(user_id=admin_id, type="like", product_id=product_id).exists()
    user_list = User.objects.all()
    engagements = Engagement.objects.all()
    status_prod = AvailedProduct.objects.filter(user_id=admin_id, product_id=product_id).values_list('status', flat=True).first() or 'none'


    # Handle like submission
    if request.method == 'POST':
    
        # Handle add feedback
        if 'add_feedback' in request.POST:
            user_id = request.POST.get('user')
            product_id = request.POST.get('product')
            content = request.POST.get('content')
            rating = request.POST.get('rating')

            if user_id and product_id and content and rating:
                new_feedback = UserProductFeedbackView(
                    user_id=user_id,
                    product_id=product_id,
                    content=content,
                    rating=rating
                )
                new_feedback.save()
                messages.success(request, "Feedback added successfully.")
            return redirect('view_product', product_id=product_id)
        elif 'delete_feedback' in request.POST:
            feedback_id = request.POST.get('feedback_id')  # Get feedback ID from form
            print(f"{feedback_id} ss")
            feedback_entry = get_object_or_404(Feedback, feedback_id=feedback_id)
            feedback_entry.delete()
            return redirect('view_product', product_id=product_id)
        elif 'purchase' in request.POST:
            AvailedProduct.objects.get_or_create( user_id=admin_id, product_id=product_id, defaults={'status': 'pending'} )
            return redirect('view_product', product_id=product_id)

            


    context = {
        'products': products,  # Products filtered by the same category
        'full_name': full_name,
        'current_url' : current_url,
        'feedback': feedback,
        'admin_id': admin_id,
        'user_list' : user_list,
        'status_prod' : status_prod,
        'role': role,
        'engagements' : engagements,
        'is_liked': is_liked,
        'product_id' : product_id,
        'admin_user': admin_user,
        'engagement_summary': engagement_summary,
        'current_product': product  # Current product being viewed
    }

    return render(request, 'views/view-product.html', context)


def current_url_view(request):
    current_url = request.get_full_path()
    return HttpResponse(f"Current URL: {current_url}")


def change_password(request, user_id):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        user = get_object_or_404(User, user_id=user_id)
        
        # Update the user's password
        user.password_hash = new_password
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



from django.db.models import Q


from django.db.models import Count
from django.db.models import F, OuterRef, Subquery

def ecom(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found

    # Subquery to get the avg_rating from AllProductsRatings
    rating_subquery = AllProductsRatings.objects.filter(
        product_id=OuterRef('product_id')
    ).values('avg_rating')[:1]

    # Count likes for each product, order by likes, and select the top 20 unique products
    top_products = Product.objects.annotate(
        like_count=Count('engagement', filter=Q(engagement__type='like')),
        avg_rating=Subquery(rating_subquery)
    ).select_related('user').order_by('-like_count')[:20]

    # Fetch categories of products that the admin has engaged with (liked or clicked)
    engaged_categories = Engagement.objects.filter(
        user_id=admin_id,
        type__in=['like', 'click']
    ).values_list('product__category', flat=True).distinct()

    # Fetch recommended products based on engaged categories (excluding products already engaged with)
    recommended_products = Product.objects.filter(
        category__in=engaged_categories
    ).select_related('user').distinct().annotate(
        avg_rating=Subquery(rating_subquery)
    )

    # Get a list of product IDs that are either in top products or recommended products
    excluded_product_ids = list(top_products.values_list('product_id', flat=True)) + \
                           list(recommended_products.values_list('product_id', flat=True))

    # Fetch products that are not in top products and recommended products
    other_products = Product.objects.exclude(
        product_id__in=excluded_product_ids
    ).select_related('user').annotate(
        avg_rating=Subquery(rating_subquery)
    )

    # Pass top products, recommended products, and other products to the template
    context = {
        'top_products': top_products,
        'recommended_products': recommended_products,
        'other_products': other_products,
        'full_name': full_name,
        'admin_id': admin_id,
        'admin_user': admin_user,
        'user_list': User.objects.all(),
        'role': role,
        'all_eng': Engagement.objects.all()
    }

    return render(request, 'views/ecom.html', context)

def ecom_top(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found


    # Count likes for each product, order by likes, and select the top 20 unique products
    top_products = TopRatedProduct.objects.all()

    

    # Pass top products, recommended products, and other products to the template
    context = {
        'top_products': top_products,
        'full_name': full_name,
        'admin_id': admin_id,
        'admin_user': admin_user,
        'user_list': User.objects.all(),
        'role': role,
        'all_eng': Engagement.objects.all()
    }

    return render(request, 'views/ecom_top.html', context)


def update_ads_status(request, product_id, status):
    product = get_object_or_404(Product, product_id=product_id)
    product.ads_status = status
    product.save()
    return redirect('products')  # Redirect to the login page



def update_ads_status_r(request, product_id, status, reason):
    product = get_object_or_404(Product, product_id=product_id)
    product.ads_status = status
    product.restriction_reason = reason
    product.save()
    return redirect('products')  # Redirect to the login page
    


def mark_product_as_available(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, product_id=product_id)
        product.is_sold = 0
        product.save()
        return JsonResponse({'success': True, 'message': 'Product marked as Available.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
    

def mark_product_as_sold(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, product_id=product_id)
        product.is_sold = 1
        product.save()
        return JsonResponse({'success': True, 'message': 'Product marked as sold.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})
    
@csrf_exempt
def update_product(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            product = Product.objects.get(pk=product_id)
            product.title = data.get('title', product.title)
            product.description = data.get('description', product.description)
            product.category = data.get('category', product.category)
            product.price = data.get('price', product.price)
            product.stock = data.get('stock', product.stock)
            product.location = data.get('location', product.location)

            product.save()
            return JsonResponse({'status': 'success', 'message': 'Product updated successfully.'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Product not found.'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})

    


@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return JsonResponse({'status': 'success'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'})
    else:
        return HttpResponseForbidden()


def save_image(image, title):
    """Helper function to save an uploaded image and return the image URL."""
    if image:
        image_folder = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
        os.makedirs(image_folder, exist_ok=True)

        # Generate the file path using the product title
        image_name = f"{title.replace(' ', '_')}_{image.name}"
        image_path = os.path.join(image_folder, image_name)

        # Save the image to the static/images folder
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Build the image URL relative to the static folder
        return f"/images/{image_name}"
    return None

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            user_id = request.POST.get('user_id')
            category = request.POST.get('category')
            price = request.POST.get('price')
            location = request.POST.get('location')

            # Validate required fields
            if not all([title, description, user_id, category, price,  location]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

            # Convert price and stock to appropriate data types
            try:
                price = float(price)  # Ensure price is a float
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid price or stock value.'})

            # Handle image uploads
            image_url = save_image(request.FILES.get('image'), title)
            image_url2 = save_image(request.FILES.get('new_ads'), title)

            # Create a new Product object and save it
            product = Product(
                title=title,
                user_id=user_id,
                description=description,
                category=category,
                price=price,
                location=location,
                image_url=image_url,
                ads_url=image_url2
            )
            product.save()

            return JsonResponse({'status': 'success', 'message': 'Product added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def product_avails(request, product_id):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    # Fetch the admin user if available
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  

    # Fetch availed products for the given product_id
    avails = AvailedProductDetailsView.objects.filter(product_id=product_id)

    if not avails.exists():
        avails = 0  # Explicitly returning an empty queryset


    if request.method == "POST":
        availed_product = AvailedProduct.objects.filter(product_id=product_id).first()
        if availed_product:  # Ensure the object exists before updating
            if "approve" in request.POST:
                availed_product.status = 'approved'
                availed_product.save()
            elif "decline" in request.POST:
                availed_product.status = 'declined'
                availed_product.save()
        return redirect('product_avails', product_id=product_id)

    context = {
        'avails': avails,
        'full_name': full_name,
        'admin_id': admin_id,
        'role': role,
        'admin_user': admin_user,
    }

    return render(request, 'views/products_avails.html', context)

def users(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

                
        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_users = User.objects.all()
    context = {'users': all_users, 'full_name': full_name, 'admin_id' : admin_id,'role': role, 'admin_user': admin_user }
    return render(request, 'views/users.html', context)

def engagements(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_engagements = Engagement.objects.all()
    users = User.objects.all()
    products = Product.objects.all()
    context = {
        'engagements': all_engagements,
        'users': users,
        'role': role,
        'products': products,
        'full_name': full_name, 'admin_id' : admin_id, 'admin_user': admin_user 
    }
    return render(request, 'views/engagement.html', context)


def feedbacks(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_feedbacks = Feedback.objects.all()
    users = User.objects.all()
    products = Product.objects.all()
    context = {'feedbacks': all_feedbacks, 
        'users': users,
        'role': role,
        'products': products, 'full_name': full_name, 'admin_id' : admin_id, 'admin_user': admin_user }
    return render(request, 'views/feedback.html', context)

def messages(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_messages = Message.objects.all()
    users = User.objects.all()
    context = {'messages': all_messages, 
        'users': users, 'full_name': full_name, 
        'role': role,'admin_id' : admin_id, 'admin_user': admin_user }
    return render(request, 'views/messages.html', context)

def profiles(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_profiles = Profile.objects.all()
    users = User.objects.all()
    context = {'profiles': all_profiles, 
        'users': users, 'full_name': full_name, 'role': role, 'admin_id' : admin_id, 'admin_user': admin_user }
    return render(request, 'views/profiles.html', context)

def support_inquiries(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    all_inquiries = SupportInquiry.objects.all()
    users = User.objects.all()
    context = {'inquiries': all_inquiries, 
        'users': users, 'full_name': full_name,'role': role, 'admin_id' : admin_id, 'admin_user': admin_user }
    return render(request, 'views/support.html', context)

@login_required
def google_login(request):
    if request.user.is_authenticated and request.user.email:
        return redirect('login')
    if request.method == "POST":
        email = request.POST.get("email")
        return JsonResponse({"email": email})  # Return email as JSON
    return render(request, "views/google_signin.html")

@login_required
@csrf_exempt  # Only if you're doing POST from frontend JavaScript or form without CSRF token
def google_login_handler(request):
    if request.method == "POST":
        # You can handle the POSTed data here if needed
        return JsonResponse({"message": request.user.email})

    # Send a POST automatically with the user's email (after login)
    user_email = request.user.email
    return render(request, 'views/google_post_login.html', {'email': user_email})


def google_logout(request):
    # Log out the user from Django
    logout(request)

    # Optional: Redirect to Google's logout endpoint if you want to log the user out from Google too
    # NOTE: This only affects SSO (Single Sign-On) if user is logged into their Google account.
    google_logout_url = 'https://accounts.google.com/Logout'

    # Or just redirect back to your homepage
    return redirect('/')  # or your custom URL

def preferences(request):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')
    preferences_data = list(RandomProductPerCategory.objects.all())
        # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)

        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found
    if request.method == 'POST':
        user =  admin_user  # or fetch user another way, like request.POST.get('user_id')

        for key in request.POST:
            # Skip CSRF token and non-product keys
            if key.isdigit():
                product_id = int(key)
                try:
                    product = Product.objects.get(pk=product_id)
                    Engagement.objects.create(
                        product=product,
                        user=user,
                        type='like'  # or 'click' depending on your context
                    )
                except Product.DoesNotExist:
                    continue
        user.is_new_user = 'no'
        user.save()
        return redirect('advertisements')  # Redirect after successful form submit
    
    # Split into chunks of 3 for carousel slides
    chunked_preferences = [preferences_data[i:i+3] for i in range(0, len(preferences_data), 3)]

    return render(request, "views/preferences.html", {
        'chunked_preferences': chunked_preferences,
        'full_name': full_name,
        'role': role,
        'admin_id': admin_id,
        'admin_user': admin_user
    })


def chat_message(request, user_id):
    full_name = request.session.get('full_name', 'Guest')
    admin_id = request.session.get('admin_id', '0')
    role = request.session.get('role', '')

    Message.objects.filter(sender=user_id, receiver=admin_id, status='delivered').update(status='read')

    # Fetch the admin user based on admin_id
    admin_user = None
    if admin_id:
        try:
            admin_user = User.objects.get(user_id=admin_id)
            if User.objects.filter(user_id=admin_id, is_new_user='yes').exists():
                return redirect('preferences')

            
        except User.DoesNotExist:
            admin_user = None  # Handle case where no admin user is found

    # Ensure admin_user exists before filtering messages
    if admin_user:
        # Filter messages where admin_id is either the sender or receiver and user_id is involved
        all_messages = Message.objects.filter(
            Q(sender_id=admin_id) | Q(receiver_id=admin_id),
            Q(sender_id=user_id) | Q(receiver_id=user_id)
        ).order_by('date_sent')  # Order by date ascending
    else:
        all_messages = Message.objects.none()  # Return an empty QuerySet if admin_user is not found

    # Separate users into senders and receivers
    senders = User.objects.filter(user_id=admin_id).distinct()
    receivers = User.objects.filter(user_id=user_id).distinct()
    sender_id = admin_id
    
    receiver_id = user_id

    users = UserMessagesView.objects.all()

    context = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'all_messages': all_messages,
        'senders': senders,
        'role': role,
        'receivers': receivers,
        'users': users,
        'full_name': full_name,
        'admin_id': admin_id,
        'admin_user': admin_user
    }
    return render(request, 'views/chatmessage.html', context)



@csrf_exempt
def update_profile_image(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)

            # Handle image upload
            image = request.FILES.get('profile_image')
            if image:
                # Use STATICFILES_DIRS or a specific directory inside the static folder
                image_folder = os.path.join(settings.BASE_DIR, 'staticfiles', 'profile_images')
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)

                # Generate the file path using a unique name
                image_name = f"{user_id}_{image.name}"
                image_path = os.path.join(image_folder, image_name)

                # Save the image to the static/images folder
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Build the image URL relative to the static folder
                image_url = f"/profile_images/{image_name}"

                # Update the user's profile_image_url
                user.profile_url = image_url
                user.save()
                

                return JsonResponse({'status': 'success', 'message': 'Profile image updated successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No image file provided.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def logout_view(request):
    logout(request)  # This will clear the session data and log out the user
    # Optional: Redirect to Google's logout endpoint if you want to log the user out from Google too
    # NOTE: This only affects SSO (Single Sign-On) if user is logged into their Google account.
    google_logout_url = 'https://accounts.google.com/Logout'

    return redirect('login')  # Redirect to the login page


@csrf_exempt
def add_user(request):
    if request.method == 'POST':
        try:
            # Handle file upload
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                # Ensure correct handling of binary file
                image_path = os.path.join(settings.BASE_DIR, 'staticfiles','profile_images', profile_image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in profile_image.chunks():
                        destination.write(chunk)
                
                # Save the file path in the database
                profile_image_url = os.path.join('profile_images', profile_image.name)
            else:
                profile_image_url = None

            # Create user object and save
            user = User(
                username=request.POST.get('username'),
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                password_hash=request.POST.get('password'),
                role=request.POST.get('role'),
                verified=request.POST.get('verified') == 'on',
                profile_url=profile_image_url
            )
            user.save()

            return JsonResponse({'status': 'success', 'message': 'User added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})





@csrf_exempt
def add_engagement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product')
            user_id = data.get('user')
            engagement_type = data.get('type')
            user = User.objects.get(pk=user_id)
            product = Product.objects.get(pk=product_id)
            engagement = Engagement(product=product, user=user, type=engagement_type)
            engagement.save()
            return JsonResponse({'status': 'success', 'message': 'Engagement added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def add_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user')
            content = data.get('content')
            rating = data.get('rating')
            product_id = data.get('product')  # Get the product_id
            
            user = User.objects.get(pk=user_id)
            product = Product.objects.get(pk=product_id)  # Get the product

            feedback = Feedback(user=user, comment=content, rating=rating, product=product)  # Include product
            feedback.save()
            return JsonResponse({'status': 'success', 'message': 'Feedback added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# Revision
from django.db import connection

@csrf_exempt
def add_message(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')
            content = data.get('content')

            # Validate sender and receiver existence
            sender = User.objects.get(pk=sender_id)
            receiver = User.objects.get(pk=receiver_id)

            # Save the message with a custom timestamp
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO messages (sender_id, receiver_id, content, date_sent)
                    VALUES (%s, %s, %s, CONVERT_TZ(NOW(), '+00:00', '+08:00'))
                    """, [sender.user_id, receiver.user_id, content]
                )

            return JsonResponse({'status': 'success', 'message': 'Message added successfully!'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sender or receiver not found'})
        except Exception as e:
            print("Error:", str(e))  # Debugging output
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        try:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return JsonResponse({'status': 'success'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Product not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt
def add_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            contact_number = data.get('contact')
            bio = data.get('bio')
            user = User.objects.get(pk=user_id)
            profile = Profile(user=user, bio=bio, contact_number=contact_number)
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Profile added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def add_support_inquiry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            subject = data.get('subject')
            status = data.get('status')
            message = data.get('message')
            user = User.objects.get(pk=user_id)
            support_inquiry = SupportInquiry(user=user, subject=subject, message=message, status=status)
            support_inquiry.save()
            return JsonResponse({'status': 'success', 'message': 'Support Inquiry added successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# Update Views
@csrf_exempt
def update_user(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.get(pk=user_id)
            user.username = data.get('username', user.username)
            user.first_name = data.get('first_name', user.first_name)
            user.middle_name = data.get('middle_name', user.middle_name)
            user.last_name = data.get('last_name', user.last_name)
            user.role = data.get('role', user.role)
            user.email = data.get('email', user.email)
            user.verified = data.get('verified', user.verified)
            user.password_hash = data.get('password', user.password_hash)
            user.email = data.get('email', user.email)
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User updated successfully!'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'User not found.'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
    
    
    
# Update Only the 'verified' Column
@csrf_exempt
def update_user_verified(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.get(pk=user_id)

            # Update only the 'verified' field
            if 'verified' in data:
                user.verified = data['verified']
                user.save()

                return JsonResponse({'status': 'success', 'message': 'User verification status updated successfully!'})
            else:
                return JsonResponse({'status': 'fail', 'message': 'Verification status not provided.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'User not found.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON data.'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})

    
    
@csrf_exempt
def update_engagement(request, engagement_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            engagement = Engagement.objects.get(pk=engagement_id)
            
            # Update the fields
            engagement.user_id = data.get('user')
            engagement.product_id = data.get('product')
            engagement.type = data.get('type')
            
            engagement.save()
            return JsonResponse({'status': 'success', 'message': 'Engagement updated successfully!'})
        except Engagement.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Engagement not found.'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
    
@csrf_exempt
def update_feedback(request, feedback_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            feedback = Feedback.objects.get(pk=feedback_id)

            user_id = data.get('user')
            product_id = data.get('product')

            if user_id:
                feedback.user = User.objects.get(pk=user_id)  # Retrieve the User instance

            if product_id:
                feedback.product = Product.objects.get(pk=product_id)  # Retrieve the Product instance

            feedback.comment = data.get('content', feedback.comment)
            feedback.rating = data.get('rating', feedback.rating)

            feedback.save()
            return JsonResponse({'status': 'success', 'message': 'Feedback updated successfully!'})
        except Feedback.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Feedback not found.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'User not found.'})
        except Product.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Product not found.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
@csrf_exempt
def update_message(request, message_id):
    if request.method in ['POST', 'PUT']:
        try:
            data = json.loads(request.body)
            message = Message.objects.get(pk=message_id)

            # Update fields as necessary
            message.content = data.get('content', message.content)
            if 'sender_id' in data:
                sender_id = data.get('sender_id')
                sender = User.objects.get(pk=sender_id)
                message.sender = sender
            if 'receiver_id' in data:
                receiver_id = data.get('receiver_id')
                receiver = User.objects.get(pk=receiver_id)
                message.receiver = receiver

            message.save()
            return JsonResponse({'status': 'success', 'message': 'Message updated successfully!'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Message not found.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sender or receiver not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
    
    
@csrf_exempt
def update_profile(request, profile_id):
    if request.method in ['POST', 'PUT']:
        try:
            data = json.loads(request.body)
            profile = Profile.objects.get(pk=profile_id)
            profile.contact_number = data.get('contact', profile.contact_number)
            profile.bio = data.get('bio', profile.bio)
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Profile not found.'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
@csrf_exempt
def update_support_inquiry(request, inquiry_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            support_inquiry = SupportInquiry.objects.get(pk=inquiry_id)

            # Update fields
            if 'subject' in data:
                support_inquiry.subject = data['subject']
            if 'message' in data:
                support_inquiry.message = data['message']
            if 'status' in data:
                support_inquiry.status = data['status']
            if 'user' in data:
                try:
                    new_user = User.objects.get(pk=data['user'])
                    support_inquiry.user = new_user
                except User.DoesNotExist:
                    return JsonResponse({'status': 'fail', 'message': 'User not found.'})

            support_inquiry.save()
            return JsonResponse({'status': 'success', 'message': 'Support Inquiry updated successfully!'})
        except SupportInquiry.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Support Inquiry not found.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON.'})
        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': str(e)})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method.'})
# Delete Views
@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(pk=user_id)
            user.delete()
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt  # If you're not using the CSRF token, use this decorator
def record_engagement(request):
    admin_id = request.session.get('admin_id', '0')
    if request.method == 'POST':
        try:
            # Parse the request body (assuming JSON format)
            data = json.loads(request.body)
            product_id = data.get('product_id')
            engagement_type = data.get('type')

            # Example logic (you would replace this with your own logic)
            if product_id and engagement_type:
                new_engagement = Engagement.objects.create(
                        product_id=product_id,
                        user_id=admin_id,
                        type=engagement_type
                    )

                    # Save the record (optional since create() automatically saves)
                new_engagement.save()
                return JsonResponse({'status': 'success', 'message': 'Engagement recorded'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Missing parameters'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_engagement(request, engagement_id):
    if request.method == 'DELETE':
        try:
            engagement = Engagement.objects.get(pk=engagement_id)
            engagement.delete()
            return JsonResponse({'status': 'success'})
        except Engagement.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Engagement not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt
def delete_feedback(request, feedback_id):
    if request.method == 'DELETE':
        try:
            feedback = Feedback.objects.get(pk=feedback_id)
            feedback.delete()
            return JsonResponse({'status': 'success'})
        except Feedback.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Feedback not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt
def delete_message(request, message_id):
    if request.method == 'DELETE':
        try:
            message = Message.objects.get(pk=message_id)
            message.delete()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt
def delete_profile(request, profile_id):
    if request.method == 'DELETE':
        try:
            profile = Profile.objects.get(pk=profile_id)
            profile.delete()
            return JsonResponse({'status': 'success'})
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile not found'})
    else:
        return HttpResponseForbidden()

@csrf_exempt
def delete_support_inquiry(request, inquiry_id):
    if request.method == 'DELETE':
        try:
            support_inquiry = SupportInquiry.objects.get(pk=inquiry_id)
            support_inquiry.delete()
            return JsonResponse({'status': 'success'})
        except SupportInquiry.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Support Inquiry not found'})
    else:
        return HttpResponseForbidden()

# Register Views in urls.py
