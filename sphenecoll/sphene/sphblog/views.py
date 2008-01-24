# blog views

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from sphene.community.middleware import get_current_urlconf
from sphene.community.sphutils import add_rss_feed
from sphene.sphboard.views import showThread as sphboard_show_thread
from sphene.sphboard.models import Category, ThreadInformation, Post
from sphene.sphblog.models import BlogPostExtension

def get_board_categories(group):
    """
    Returns a list of all categories of type 'sphblog'
    """
    # First fetch all categories matching the group and type.
    categories = Category.objects.filter( category_type = 'sphblog' )
    # Now check permissions
    blogcategories = filter(Category.has_view_permission, categories)
    return blogcategories

def get_posts_queryset(group, categories):
    threads = Post.objects.filter( thread__isnull = True,
                                   category__group__id = group.id,
                                   category__id__in = map(lambda x: x.id, categories) ).order_by( '-postdate' )
    return threads

def blogindex(request, group):
    categories = get_board_categories(group)
    if not categories:
        return render_to_response( 'sphene/sphblog/nocategory.html',
                                   { },
                                   context_instance = RequestContext(request) )

    threads = get_posts_queryset(group, categories)

    allowpostcategories = filter(Category.has_post_thread_permission, categories)
    blog_feed_url = reverse('sphblog-feeds', urlconf=get_current_urlconf(), args = ('latestposts',), kwargs = { 'groupName': group.name })
    add_rss_feed( blog_feed_url, 'Blog RSS Feed' )
    return render_to_response( 'sphene/sphblog/blogindex.html',
                               { 'allowpostcategories': allowpostcategories,
                                 'threads': threads,
                                 'blog_feed_url': blog_feed_url,
                                 },
                               context_instance = RequestContext(request) )


def postthread(request, group):
    category_id = request.POST['category']
    category = Category.objects.get( pk = category_id )

    return HttpResponseRedirect( category.get_absolute_post_thread_url() )


def show_thread(request, group, slug, year = None, month = None, day = None):
    try:
        blogpost = BlogPostExtension.objects.get( slug__exact = slug )
    except BlogPostExtension.DoesNotExist:
        raise Http404
    return sphboard_show_thread( request, blogpost.post.id, group )

