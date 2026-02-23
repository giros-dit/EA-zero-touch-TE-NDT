terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}
provider "openstack" {
  auth_url             = "http://10.0.10.250:5000/v3"
  user_name            = "admin"
  password             = "xxxx"
#  region              = "RegionOne"
  user_domain_name     = "Default"
  project_domain_name  = "Default"
  tenant_name          = "admin"
}

resource "openstack_networking_network_v2" "my_network" {
  name = "my_network"
    admin_state_up = true
}
# Definicion del router
resource "openstack_networking_router_v2" "r1" {
  name = "r1"
  admin_state_up = true
}
# Definicion de la subred
resource "openstack_networking_subnet_v2" "subnet" {
  name            = "subnet"
  network_id      = openstack_networking_network_v2.my_network.id
  cidr            = "10.0.0.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
}

# Asociar la subred al router
resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id     = openstack_networking_router_v2.r1.id
  subnet_id     = openstack_networking_subnet_v2.subnet.id
}

resource "openstack_compute_keypair_v2" "my_keypair" {
  name       = "my_keypair"
  public_key = file("./mykey.pub")
}


# Definicion de la instancia de maquina virtual
resource "openstack_compute_instance_v2" "vm1" {
  name              = "vm1"
  image_name        = "cirros-0.3.4-x86_64-vnx"
  flavor_name       = "m1.tiny"
  key_pair          = openstack_compute_keypair_v2.my_keypair.name
  network {
    name = openstack_networking_network_v2.my_network.name
  }
}
