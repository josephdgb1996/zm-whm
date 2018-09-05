#!/usr/bin/perl
system("clear");
use strict;
use warnings;
use File::Copy;
print "Installing the Zoho Mail WHM Plugin...\n";

# Create the directory for the plugin
print "Creating /usr/local/cpanel/whostmgr/docroot/cgi/zohomail directory... ";
mkdir "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail";
mkdir "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets";
mkdir "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images";
print " - Done\n";

# # Obtain the plugin from Github
# print "Downloading whmrblcheck.tar.gz... ";
# my $download = qx[ curl --silent https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/whmrblcheck.tar.gz > "/root/whmrblcheck.tar.gz" ];
# print " - Done\n";

# # Uncompress whmrblcheck.tar.gz
# print "Extracting whmrblcheck.tar.gz... ";
# my $tar = Archive::Tar->new;
# $tar->read("/root/whmrblcheck.tar.gz");
# $tar->extract();
# print " - Done\n";

# Copy the zohomail.jpg (Icon) image file to /usr/local/cpanel/whostmgr/docroot/addon_plugins
print "Copying zohomail.png to /usr/local/cpanel/whostmgr/docroot/addon_plugins... ";
copy("zohomail.png","/usr/local/cpanel/whostmgr/docroot/addon_plugins") or die "Copy failed: $!";
print " - Done\n";

# Copy the zohomail.cgi file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying zohomail.cgi to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail... ";
copy("zohomail.cgi","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail") or die "Copy failed: $!";
print " - Done\n";

# Copy the arrow.svg file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying arrow.svg to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images... ";
copy("assets/images/arrow.svg","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images") or die "Copy failed: $!";
print " - Done\n";

# Copy the dropdown.png file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying dropdown.png to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images... ";
copy("assets/images/dropdown.png","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images") or die "Copy failed: $!";
print " - Done\n";

# Copy the success.svg file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying success.svg to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images... ";
copy("assets/images/success.svg","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images") or die "Copy failed: $!";
print " - Done\n";

# Copy the error.svg file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying error.svg to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images... ";
copy("assets/images/error.svg","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images") or die "Copy failed: $!";
print " - Done\n";

# Copy the dropdown.png file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying zoho.png to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images... ";
copy("assets/images/zoho.png","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/images") or die "Copy failed: $!";
print " - Done\n";

# Copy the style.css file to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail
print "Copying style.css to /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/... ";
copy("assets/style.css","/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets") or die "Copy failed: $!";
print " - Done\n";

# Set execute permissions on the zohomail.cgi script
print "Setting permissions on /usr/local/cpanel/whostmgr/docroot/cgi/zohomail/zohomail.cgi to 0755...";
chmod 0755, "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/zohomail.cgi";
chmod 0755 , "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/assets/style.css";
chmod 0755 , "/usr/local/cpanel/whostmgr/docroot/cgi/zohomail/images";
print " - Done\n";

#copy the zohomail.pm to /var/cpanel...
print "Copying the ZohoMail.pm to /usr/local/cpanel";
copy("ZohoMail.pm","/usr/local/cpanel") or die "Copy failed: $!";
chmod 0755, "/usr/local/cpanel/ZohoMail.pm";
print " -Done\n";

#register the hook
print "Registering hook through module";
system("/usr/local/cpanel/bin/manage_hooks add module ZohoMail");
print " -Done\n";

# Register the plugin
print "Registering plugin...";
system( "/usr/local/cpanel/bin/register_appconfig zohomail.conf" );

print "\nZoho Mail WHM Plugin installed!\n";
exit;


