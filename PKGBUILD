# Maintainer: 0xsapphir3 <0xsapphir3@gmail.com>

pkgname=galleryman-git
pkgver=0.1
pkgrel=1
provides=("${pkgname%-git}")
conflicts=("${pkgname%-git}")
pkgdesc="Gallery written in Python for managing your photos"
url="https://github.com/0xsapphir3/GalleryMan"
arch=("any")
license=("MIT")
depends=("python>=3.6" "python-setuptools" )
source=("git+https://github.com/0xsapphir3/GalleryMan.git")
md5sums=("SKIP")

pkgver()
{
  cd "${pkgname%-git}"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package()
{
  cd "${pkgname%-git}"
  python setup.py install --optimize="1" --root="$pkgdir"
}
