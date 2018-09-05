BEGIN {
    unshift @INC, '/usr/local/cpanel';
    unshift @INC, '/usr/local/cpanel/scripts';
    unshift @INC, '/usr/local/cpanel/bin';
    unshift @INC, '/usr/local/share/perl5';
}
package ZohoMail;
use strict;
use Data::Dumper;
use warnings;
use JSON;
use Cpanel::Logger;
use Whostmgr::NVData;
use LWP::UserAgent;
use HTTP::Request;
use MIME::Base64;
my $logger = Cpanel::Logger->new();
sub describe {
    my $my_add = [
        {
            'category' => 'Whostmgr',
            'event'    => 'Accounts::Create',
            'stage'    => 'post',
            'hook'     => 'ZohoMail::createorg',
            'exectype' => 'module',
        }
    ];
    return $my_add;
}

sub createorg {
# Get the data that the system passes to the hook.
    my ( $context, $data ) = @_;                
 
    # Set success and failure messages.
    my $result  = 0;                             # This boolean value is set to fail.    
    my $message = 'This is an error message.';   # This string is a reason for $result.
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#creating the child organization when user is created in cPanel. Collecting the reseller details from the NVData.

#Step 1: Fetching the params of the create account action.

    $logger->info($data->{'user'});
    $logger->info($data->{'domain'});
    my $emailId;
    if ( length $data->{'contactemail'}) {
        $logger->info($data->{'contactemail'});
        $emailId = $data->{'contactemail'};
    } else {
        $emailId = 'admin@'.$data->{'domain'};
    }
#---------------------------------------------------------------------------------
#Step 2: Taking the reseller details.

    my @resellerval = split(/__/,Whostmgr::NVData::get("reseller_details"));


#---------------------------------------------------------------------------------
#Step 3: Preparing the necessary parameters for URL call of creating child organization.

    my $urlOrganization = "https://mail.zoho".$resellerval[0]."/api/organization";
    my %json_string = ('domainName' => $data->{'domain'}, 'emailId' => $emailId, 'firstName' => $data->{'user'}, 'lastName' => $data->{'user'});
    my $json_body = encode_json \%json_string;   #Constructing the json body for creating the child organization


#----------------------------------------------------------------------------------
#Step 4: Updating the access token if neccessary to make the URL call

    my $access_token;
    if (time()- Whostmgr::NVData::get("ZM_TIMESTAMP") > 3000) {
        $access_token = ZohoMail::fetchaccesstoken();
    } else {
        $access_token = decode_base64($resellerval[5]);
    }
#-----------------------------------------------------------------------------------
#step 5: Necessary Debug Logs.

    $logger->info(time()- Whostmgr::NVData::get("ZM_TIMESTAMP"));
    if(length $access_token) {
        $logger->info("Good to GO!!");
    }
    if ($access_token eq "123") {
        $logger->info("Fetching access token failed");
    }
    $logger->info($json_body);
    $logger->info($urlOrganization);


#------------------------------------------------------------------------------------
#Step 6: Implementing the POST requst.


    my $ua = new LWP::UserAgent;
    my $req = new HTTP::Request POST => $urlOrganization;
    $req->header('Content-Type' => 'application/json');
    $req->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
    $req->content($json_body);
    my $res = $ua->request($req);
    if ($res->is_success) { 
        my $decoderesp_json = decode_json($res->content);
        $logger->info($res->content);
        my $zoid = $decoderesp_json->{'data'}->{'zoid'};
        $logger->info($zoid);
        if (length $zoid) {
            Whostmgr::NVData::set("zm_resellerorgs",$zoid."__".$data->{'domain'}."__".Whostmgr::NVData::get("zm_resellerorgs"));
            $result = 1;
            $message = 'Org creation Success';
            } 
        else {
                $result = 0;
                $message = 'Org Creation Failed';
                $logger->info($decoderesp_json);
            }
    } else {
        $logger->info($res->status_line);
        $logger->info($res->content);
        $result = 0;
        $message = 'Org Creation Failed';
    }

     $logger->info(Whostmgr::NVData::get("zm_resellerorgs"));

#---------------------------------------------------------------------------------------------
    return $result, $message;
}

sub fetchaccesstoken {
    my @resellerval = split(/__/,Whostmgr::NVData::get("reseller_details"));
    my $fetchaccesstokenurl = "https://accounts.zoho".$resellerval[0]."/oauth/v2/token?refresh_token=".decode_base64($resellerval[4])
                                 ."&grant_type=refresh_token&client_id=".$resellerval[1]
                                 ."&client_secret=".$resellerval[2]
                                 ."&redirect_url=".$resellerval[3]
                                 ."&scope=VirtualOffice.partner.organization.CREATE,VirtualOffice.partner.organization.READ,VirtualOffice.organization.READ";
    my $ua = new LWP::UserAgent;
    my $req = new HTTP::Request POST => $fetchaccesstokenurl;
    my $res = $ua->request($req);
    if ($res->is_success) {
        my $decodedresponse = decode_json($res->content);
        if (length $decodedresponse->{'access_token'}) {
            Whostmgr::NVData::set("reseller_details",$resellerval[0]."__".$resellerval[1]
                                        ."__".$resellerval[2]."__".$resellerval[3]
                                        ."__".$resellerval[4]."__".encode_base64($decodedresponse->{'access_token'}));
            Whostmgr::NVData::set("ZM_TIMESTAMP",time());
            return $decodedresponse->{'access_token'};
        }
        } else {
             $logger->info($res->status_line);    
             $logger->info($res->content);
             return "123";
        }
 
}

1;
