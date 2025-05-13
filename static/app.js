angular
  .module("marketplaceApp", [])
  .config([
    "$httpProvider",
    function ($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = "csrftoken";
      $httpProvider.defaults.xsrfHeaderName = "X-CSRFToken";
    },
  ])
  .controller("MainController", [
    "$scope",
    "$http",
    function ($scope, $http) {
      // Initialize variables
      $scope.isAuthenticated = false;
      $scope.username = "";
      $scope.loginData = { username: "", password: "" };
      $scope.loginError = "";
      $scope.products = [];
      $scope.recommendations = [];
      $scope.recommendationsMessage = "";
      $scope.viewedProducts = [];
      $scope.unviewedProducts = [];
      $scope.browsingHistory = [];
      $scope.clicks = [];
      $scope.apiError = "";
      $scope.filterError = "";
      $scope.clickSuccessMessage = "";
      $scope.filters = { minPrice: null, maxPrice: null, category: "" };
      $scope.isLoading = false;

      // Fetch CSRF token
      $scope.getCsrfToken = function () {
        $scope.isLoading = true;
        return $http
          .get("/api/get-csrf-token/")
          .then(
            function (response) {
              console.log("CSRF token fetched:", response.data);
              return response.data;
            },
            function (error) {
              console.error("Error fetching CSRF token:", error);
              $scope.apiError = "Failed to fetch CSRF token.";
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Check authentication status
      $scope.checkAuth = function () {
        $scope.isLoading = true;
        $http
          .get("/api/products/")
          .then(
            function (response) {
              $scope.isAuthenticated = true;
              $scope.username = $scope.loginData.username || "User";
              $scope.fetchProducts();
              $scope.fetchRecommendations();
              $scope.fetchRecommendationClicks();
              $scope.fetchBrowsingHistory();
            },
            function (error) {
              $scope.isAuthenticated = false;
              $scope.username = "";
              $scope.apiError = "Please log in to view products.";
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Login function
      $scope.login = function () {
        $scope.loginError = "";
        $scope.isLoading = true;
        $http({
          method: "POST",
          url: "/accounts/login/",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          transformRequest: function (obj) {
            var str = [];
            for (var p in obj) {
              str.push(
                encodeURIComponent(p) + "=" + encodeURIComponent(obj[p])
              );
            }
            return str.join("&");
          },
          data: $scope.loginData,
        })
          .then(
            function () {
              $scope.checkAuth();
            },
            function (error) {
              $scope.loginError =
                error.status === 401
                  ? "Invalid username or password."
                  : "Login failed: " + (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Logout function
      $scope.logout = function () {
        $scope.isLoading = true;
        $http
          .post("/accounts/logout/")
          .then(
            function () {
              $scope.isAuthenticated = false;
              $scope.username = "";
              $scope.products = [];
              $scope.recommendations = [];
              $scope.recommendationsMessage = "";
              $scope.viewedProducts = [];
              $scope.unviewedProducts = [];
              $scope.browsingHistory = [];
              $scope.clicks = [];
              $scope.clickSuccessMessage = "";
              $scope.apiError = "";
            },
            function (error) {
              $scope.apiError = "Logout failed.";
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Fetch all products
      $scope.fetchProducts = function () {
        $scope.apiError = "";
        $scope.isLoading = true;
        $http
          .get("/api/products/")
          .then(
            function (response) {
              $scope.products = response.data.products.map(function (p) {
                p.price = parseFloat(p.price);
                return p;
              });
            },
            function (error) {
              $scope.apiError =
                "Failed to load products: " +
                (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // View a product (save to browsing history)
      $scope.viewProduct = function (productId) {
        $scope.isLoading = true;
        $http
          .post("/api/browsing-history/", { product_id: productId })
          .then(
            function () {
              $scope.fetchRecommendations();
              $scope.fetchBrowsingHistory();
            },
            function (error) {
              $scope.apiError =
                "Failed to save browsing history: " +
                (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Fetch recommendations
      $scope.fetchRecommendations = function () {
        $scope.apiError = "";
        $scope.filterError = "";
        $scope.clickSuccessMessage = "";
        $scope.isLoading = true;

        if (
          $scope.filters.minPrice &&
          $scope.filters.maxPrice &&
          Number($scope.filters.minPrice) > Number($scope.filters.maxPrice)
        ) {
          $scope.filterError = "Min price cannot exceed max price.";
          $scope.isLoading = false;
          return;
        }

        var params = {};
        if ($scope.filters.minPrice) params.min_price = $scope.filters.minPrice;
        if ($scope.filters.maxPrice) params.max_price = $scope.filters.maxPrice;
        if ($scope.filters.category) params.category = $scope.filters.category;

        $http
          .get("/api/recommendations/", { params: params })
          .then(
            function (response) {
              $scope.recommendations = (
                response.data.recommendations || []
              ).map(function (p) {
                p.price = parseFloat(p.price);
                return p;
              });
              $scope.viewedProducts = (response.data.viewed_products || []).map(
                function (p) {
                  p.price = parseFloat(p.price);
                  return p;
                }
              );
              $scope.unviewedProducts = (
                response.data.unviewed_products || []
              ).map(function (p) {
                p.price = parseFloat(p.price);
                return p;
              });
              $scope.recommendationsMessage =
                response.data.message || "No recommendations available.";
            },
            function (error) {
              $scope.apiError =
                error.status === 403
                  ? "Please log in to view recommendations."
                  : "Failed to load recommendations: " +
                    (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Click a recommendation
      $scope.clickRecommendation = function (productId) {
        $scope.isLoading = true;
        $scope.clickSuccessMessage = "";
        $http
          .post("/api/recommendation-click/", { product_id: productId })
          .then(
            function () {
              $scope.clickSuccessMessage = "Recommendation clicked!";
              $scope.fetchRecommendationClicks();
            },
            function (error) {
              $scope.apiError =
                "Failed to log recommendation click: " +
                (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Fetch recommendation clicks
      $scope.fetchRecommendationClicks = function () {
        $scope.apiError = "";
        $scope.isLoading = true;
        $http
          .get("/api/recommendation-click/")
          .then(
            function (response) {
              $scope.clicks = (response.data.clicks || []).map(function (c) {
                c.price = parseFloat(c.price);
                return c;
              });
            },
            function (error) {
              $scope.apiError =
                "Failed to load recommendation clicks: " +
                (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Fetch browsing history
      $scope.fetchBrowsingHistory = function () {
        $scope.apiError = "";
        $scope.isLoading = true;
        $http
          .get("/api/browsing-history/")
          .then(
            function (response) {
              $scope.browsingHistory = (response.data.history || []).map(
                function (h) {
                  h.price = parseFloat(h.price);
                  return h;
                }
              );
            },
            function (error) {
              $scope.apiError =
                "Failed to load browsing history: " +
                (error.data?.detail || "Unknown error");
            }
          )
          .finally(function () {
            $scope.isLoading = false;
          });
      };

      // Clear filters
      $scope.clearFilters = function () {
        $scope.filters = { minPrice: null, maxPrice: null, category: "" };
        $scope.filterError = "";
        $scope.fetchRecommendations();
      };

      // Initialize
      $scope.getCsrfToken().then(function () {
        $scope.checkAuth();
      });
    },
  ])
  .directive("appNavbar", function () {
    return {
      restrict: "E",
      template: `
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="#">Marketplace</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item" ng-if="isAuthenticated">
                                <span class="nav-link">Welcome, {{ username }}</span>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/admin/" target="_blank">Admin</a>
                            </li>
                            <li class="nav-item" ng-if="isAuthenticated">
                                <button class="nav-link btn btn-link" ng-click="logout()">Logout</button>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        `,
    };
  })
  .directive("appFooter", function () {
    return {
      restrict: "E",
      template: `
            <footer class="bg-dark text-white text-center py-3 mt-4">
                <div class="container">
                    <p>© 2025 Marketplace. All rights reserved.</p>
                    <p>
                        <a href="#" class="text-white">About</a> |
                        <a href="#" class="text-white">Contact</a> |
                        <a href="#" class="text-white">Privacy Policy</a>
                    </p>
                </div>
            </footer>
        `,
    };
  });
