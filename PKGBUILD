# Maintainer: 0xsapphir3 <0xsapphir3@gmail.com>
pkgname=galleryman
pkgver=0.1
pkgrel=1
provides=("galleryman")
conflicts=("galleryman")
pkgdesc="Gallery written in Python for managing your photos"
url="https://github.com/0xsapphir3/GalleryMan"
arch=("any")
license=("MIT")
depends=("python>=3.6" "python-setuptools" )
source=("git+https://github.com/0xsapphir3/GalleryMan.git")
md5sums=("SKIP")

build() {
  cd "${srcdir}/${pkgname}"  
  python setup.py build
}

prepare() {
  cd "${srcdir}/${pkgname}-${pkgver}"
  python3 setup.py install --root="$pkgdir" --optimize=1 || return 1
}

package() {
  cd galleryman-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1
  ln -s galleryman "$pkgdir"/usr/bin/galleryman3
}