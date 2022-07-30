"""
This views function will capture and return the required views by the user.
"""


# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .forms import EmailPostForm
from .models import Post


# Views function for blog

# def post_list(request):
#     object_list = Post.objects.all()
#     paginator = Paginator(object_list, 3)  # 3 Posts per page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         posts = paginator(paginator.num_pages)
#
#     return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

class PostListView(ListView):
    """
    Function to display all the posts divided into pages, 3 per page for now. Pages are created using the
    paging feature provided by django. Only those posts will be displayed whose status is set to `posted`.

    **Parameters**

    Input parameters:

        :parameter ListView: Fetch the current list view of function.

    View Returns:

        :return Render: (:template:`blog/post/list.html`). This view function returns a rendered html page whose
            template is mentioned in ``template_name`` variable of the function.

    **Models**

        ``Post``
            An instance of :model:`blog.Post`.

    **Templates**

        :template:`blog/post/list.html`
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')

    if request.metod == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # send email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form})