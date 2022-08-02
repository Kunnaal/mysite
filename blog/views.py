"""
This views function will capture and return the required views by the user.
"""


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
# from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count
from django.conf import settings
from taggit.models import Tag
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


# Views function for blog

def post_list(request, tag_slug=None):
    """
    Function to display all the posts divided into pages, 3 per page for now. Pages are created using the
    paging feature provided by django. Only those posts will be displayed whose status is set to `posted`.

    **Parameters**

    Input parameters:

        :parameter request: Fetch the request object from django call that contains the header and body tags, etc.
        :parameter tag_slug: If this parameter is provided, then only posts with the mentioned tags are supplied.

    View Returns:

        :return Render: (:template:`blog/post/list.html`). This view function returns a rendered html page whose
            template is mentioned in second variable of render function.

    **Models**

        ``Post``
            An instance of :model:`blog.Post`.

    **Templates**

        :template:`blog/post/list.html`
    """
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)  # 3 Posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})

# class PostListView(ListView):
#     """
#     Function to display all the posts divided into pages, 3 per page for now. Pages are created using the
#     paging feature provided by django. Only those posts will be displayed whose status is set to `posted`.
#
#     **Parameters**
#
#     Input parameters:
#
#         :parameter ListView: Fetch the current list view of function.
#
#     View Returns:
#
#         :return Render: (:template:`blog/post/list.html`). This view function returns a rendered html page whose
#             template is mentioned in ``template_name`` variable of the function.
#
#     **Models**
#
#         ``Post``
#             An instance of :model:`blog.Post`.
#
#     **Templates**
#
#         :template:`blog/post/list.html`
#     """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = False

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment object but dont save to DB
            new_comment = comment_form.save(commit=False)
            # Assign current post to comment
            new_comment.post = post
            # Save comment to DB
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment,
                                                     'comment_form': comment_form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you to read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_SENDER, [cd['to']], fail_silently=False)
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, "sent": sent})
