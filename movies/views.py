from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Movie, Review


def index(request):
    """List movies (with optional search)."""
    search_term = request.GET.get('search', '').strip()
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {
        'title': 'Movies',
        'movies': movies,
        'search': search_term,
    }
    return render(request, 'movies/index.html', {'template_data': template_data})


def show(request, id):
    movie =  Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
        {'template_data': template_data})

@login_required
def create_review(request, id):
    """Create a review for a movie (POST only)."""
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        if comment:
            movie = get_object_or_404(Movie, id=id)
            Review.objects.create(
                comment=comment,
                movie=movie,
                user=request.user
            )
    return redirect('movies.show', id=id)


@login_required
def edit_review(request, id, review_id):
    """Edit an existing review you own."""
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {
            'title': 'Edit Review',
            'review': review,
        }
        return render(request, 'movies/edit_review.html', {'template_data': template_data})

    # POST
    comment = request.POST.get('comment', '').strip()
    if comment:
        review.comment = comment
        review.save()
    return redirect('movies.show', id=id)


@login_required
def delete_review(request, id, review_id):
    """Delete an existing review you own."""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
